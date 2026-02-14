import asyncio
import json
import os
import secrets
from datetime import datetime as dt
from datetime import timedelta as td

from dotenv import load_dotenv
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton as BButton
from telebot.types import InlineKeyboardMarkup as BMarkup
from telebot.types import Message

import db
import ssh

from redis_client import init_redis, close_redis
from translation import tr

# Load configuration
load_dotenv()


def required_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env var: {name}")
    return val.strip()


TOKEN = required_env("TOKEN")
PROVIDER_TOKEN = required_env("PROVIDER_TOKEN")
CONF_DIR = os.getenv("CONF_DIR", "./configs")
REFERAL_ALPHABET = required_env("REFERAL_SYMBOLS")
ADMIN = int(required_env("ADMIN_ID"))
cfg_tariff = {"1mo": 8000, "7d": 3000}
base_price = 70
tariff_multip = {
    1: 100,
    2: 100,
    3: 95,
    4: 95,
    5: 95,
    6: 90,
    7: 90,
    8: 90,
    9: 85,
    10: 85,
    11: 85,
}
db_host = os.getenv("DB_HOST")
db_port = int(os.getenv("DB_PORT"))  # type: ignore
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_table = os.getenv("DB_TABLE")

pay_operations = dict()
conf_changes = dict()
configs_extends = dict()
balance_depos = []
referals = []

# Initialize bot
bot = AsyncTeleBot(TOKEN, parse_mode="HTML")


# Command Handlers
@bot.message_handler(commands=["start", "s"])
async def send_start(m):
    u = await db.fetchone(
        "SELECT id, referal, locale FROM users WHERE tg_user_id=%s", (m.from_user.id,)
    )
    if not u:
        code = "".join(secrets.choice(REFERAL_ALPHABET) for _ in range(16))
        while await db.fetchone("SELECT id FROM users WHERE referal_code=%s", (code,)):
            code = "".join(secrets.choice(REFERAL_ALPHABET) for _ in range(16))
        new_uid = await db.execute(
            "INSERT INTO users (tg_user_id, username, first_name, last_name, referal_code) VALUES (%s, %s, %s, %s, %s)",
            (
                m.from_user.id,
                m.from_user.username,
                m.from_user.first_name,
                m.from_user.last_name,
                code,
            ),
        )
        mess = m.text.split(maxsplit=1)
        ref = mess[1] if len(mess) > 1 else None
        text = await tr("START_MESS", "ru")
        await bot.send_message(text=text, chat_id=m.chat.id)
        if ref:
            user = await db.fetchone(
                "SELECT first_name, id FROM users WHERE referal_code=%s", (ref,)
            )
            if user and user["id"]:
                await db.execute(
                    "UPDATE users SET referal=%s WHERE id=%s", (ref, new_uid)
                )
                text = (await tr("REFERAL_BECAME", "ru")).format(
                    user=user["first_name"]
                )
                await bot.send_message(text=text, chat_id=m.chat.id)
    else:
        await db.execute(
            "UPDATE users SET username=%s, first_name=%s, last_name=%s WHERE tg_user_id=%s",
            (
                m.from_user.username,
                m.from_user.first_name,
                m.from_user.last_name,
                m.from_user.id,
            ),
        )

        text = await tr("START_MESS", u["locale"])
        await bot.send_message(text=text, chat_id=m.chat.id)
    user_id = u["id"] if u else new_uid
    if user_id:
        await clear(user_id)
    await bot.send_message(
        chat_id=ADMIN, text=f"{m.from_user.first_name}({m.from_user.id}) pressed /start"
    )


@bot.message_handler(commands=["menu", "m"])
async def send_menu(m):
    u = await db.fetchone(
        "SELECT id, locale, balance, configs_count FROM users WHERE tg_user_id=%s",
        (m.from_user.id,),
    )
    if not u:
        text = await tr("NOT_USER", "en")
        return await bot.send_message(text=text, chat_id=m.chat.id)
    else:
        keyboard = BMarkup()
        keyboard.row(
            BButton(text=await tr("MY_CFGS", u["locale"]), callback_data="menu_cfg")
        )
        keyboard.row(
            BButton(
                text=await tr("FREE_PRESENT", u["locale"]),
                callback_data="choose_location_free",
            )
        )
        keyboard.row(
            BButton(text=await tr("ACCOUNT", u["locale"]), callback_data="menu_account")
        )
        keyboard.row(
            BButton(
                text=await tr("INFO", u["locale"]), callback_data="menu_information"
            )
        )
        keyboard.row(
            BButton(
                text=await tr("BUY_CFG", u["locale"]),
                callback_data="choose_location_buy",
            )
        )
        keyboard.row(
            BButton(text=await tr("DEPOSIT", u["locale"]), callback_data="baldeposit")
        )
        keyboard.row(
            BButton(
                text=await tr("LANG_CHANGE", u["locale"]),
                callback_data="choose_language",
            )
        )
        text = (await tr("MENU_MESS", u["locale"])).format(
            balance=u["balance"], count=u["configs_count"]
        )
        await bot.send_message(text=text, chat_id=m.chat.id, reply_markup=keyboard)
    await clear(u["id"])


@bot.message_handler(commands=["help", "h"])
async def send_help(m):
    u = await db.fetchone(
        "SELECT id, locale, admin_lvl FROM users WHERE tg_user_id=%s", (m.from_user.id,)
    )
    if not u:
        text = await tr("NOT_USER", "en")
        return await bot.reply_to(text=text, message=m)
    text = await tr("HELP", u["locale"])
    if u["admin_lvl"] > 0:
        text += await tr("ADMIN_HELP", u["locale"])
    await bot.send_message(text=text, chat_id=m.chat.id)
    await clear(u["id"])


@bot.message_handler(commands=["ref", "referal"])
async def send_referal(m):
    u = await db.fetchone(
        "SELECT id, locale, referal FROM users WHERE tg_user_id=%s",
        (m.from_user.id,),  # type: ignore
    )  # type: ignore
    if not u:
        text = await tr("NOT_USER")
        return await bot.reply_to(text=text, message=m)
    else:
        if u["referal"]:
            text = await tr("ALREADY_REFERAL", u["locale"])
            return await bot.send_message(text=text, chat_id=m.chat.id)
        try:
            code = m.text.split(" ", maxsplit=1)[1]  # type: ignore
            user = await db.fetchone(
                "SELECT first_name, id FROM users WHERE referal_code=%s", (code,)
            )
            if user and not u["referal"] and code != "site":
                await db.execute(
                    "UPDATE users SET referal=%s WHERE id=%s", (code, u["id"])
                )
                referals.remove(u["id"])
                text = (await tr("REFERAL_BECAME", u["locale"])).format(
                    user=user["first_name"]
                )
                await bot.send_message(text=text, chat_id=m.chat.id)
            else:
                text = await tr("REFERAL_ERR", u["locale"])
                await bot.send_message(text=text, chat_id=m.chat.id)
        except Exception:
            referals.append(u["id"])
            text = await tr("INPUT_REFERAL", u["locale"])
            await bot.send_message(text=text, chat_id=m.chat.id)


@bot.message_handler(commands=["a"])
async def operat(m):
    u = await db.fetchone(
        "SELECT id, admin_lvl FROM users WHERE tg_user_id=%s", (m.from_user.id,)
    )
    if not u or u["admin_lvl"] < 0:
        text = await tr("ACESS_ERR", "en")
        return await bot.send_message(text=text, chat_id=m.chat.id)
    else:
        text = (
            "Operations:\n"
            "=================\n"
            "pay_op: " + str(pay_operations) + "\n"
            "conf_changes: " + str(conf_changes) + "\n"
            "balance_depos: " + str(balance_depos) + "\n"
            "referals: " + str(referals)
        )
        await bot.send_message(m.chat.id, text)
        await bot.send_message(m.chat.id, str(dt.now()))


@bot.message_handler(commands=["sendall"])
async def sendall(m):
    u = await db.fetchone(
        "SELECT id, admin_lvl, locale FROM users WHERE tg_user_id=%s", (m.from_user.id,)
    )
    if not u or u["admin_lvl"] < 1:
        text = await tr("ACESS_ERR")
        return await bot.send_message(m.chat.id, text)
    else:
        text = m.text.replace("/sendall ", "")
        rows = await db.fetchall(
            "SELECT tg_user_id FROM users WHERE status='active' and notifications = 1"
        )
        for row in rows:
            try:
                await bot.send_message(chat_id=row["tg_user_id"], text=text)
                await asyncio.sleep(0.1)
            except Exception:
                pass


@bot.message_handler(commands=["ssh"])
async def ssh_test(m):
    u = await db.fetchone(
        "SELECT id, admin_lvl, locale FROM users WHERE tg_user_id=%s", (m.from_user.id,)
    )
    if not u or u["admin_lvl"] < 1:
        text = await tr("ACESS_ERR", "en")
        return await bot.send_message(text=text, chat_id=m.chat.id)
    else:
        text = m.text.replace("/ssh ", "")
        if text == "getkey":
            locs = await db.fetchall(
                "SELECT id, host, key_path, directory FROM locations"
            )
            for loc in locs:
                await ssh.gen_key(loc["host"], loc["key_path"], loc["directory"])
                cfgs = await db.fetchall(
                    "SELECT code_name FROM configs WHERE location_id=%s AND status = 'active'",
                    (loc["id"],),
                )
                for cfg in cfgs:
                    if loc["host"] not in ("127.0.0.1", "localhost"):
                        await ssh.get_key(
                            loc["host"],
                            loc["key_path"],
                            loc["directory"],
                            cfg["code_name"],
                        )
                    await asyncio.sleep(0.1)
            return await bot.send_message(m.chat.id, "all done")


@bot.message_handler(commands=["test"])
async def test(m):
    u = await db.fetchone(
        "SELECT id, admin_lvl, locale FROM users WHERE tg_user_id=%s", (m.from_user.id,)
    )
    if not u or u["admin_lvl"] < 1:
        text = await tr("ACESS_ERR", "en")
        return await bot.send_message(text=text, chat_id=m.chat.id)
    else:
        await bot.send_message(m.chat.id, m.text)
        print(m)


@bot.message_handler(commands=["sendto"])
async def sendto(m):
    u = await db.fetchone(
        "SELECT id, admin_lvl, locale FROM users WHERE tg_user_id=%s", (m.from_user.id,)
    )
    if not u or u["admin_lvl"] < 1:
        text = await tr("ACESS_ERR", "en")
        return await bot.send_message(text=text, chat_id=m.chat.id)
    else:
        row = m.text.split(maxsplit=2)
        user, text = row[1], row[2]
        user = await db.fetchone(
            "SELECT id, username, first_name, tg_user_id FROM users WHERE tg_user_id=%s OR username=%s",
            (user, user.lstrip("@")),
        )
        if user:
            try:
                await bot.send_message(user["tg_user_id"], text)
                await bot.send_message(m.chat.id, "Done")
            except Exception:
                await bot.send_message(m.chat.id, "Error sending message to user")
        else:
            await bot.send_message(m.chat.id, "User not found")


@bot.message_handler(
    content_types=["photo"],
    chat_types=["private"],
    func=lambda m: m.caption
    and any(
        [
            m.caption.startswith(i)
            for i in (
                "/sendto",
                "/reply",
            )
        ]
    ),
)
async def sendto_photo(m):
    u = await db.fetchone(
        "SELECT id, admin_lvl, locale FROM users WHERE tg_user_id=%s", (m.from_user.id,)
    )
    if not u or u["admin_lvl"] < 1:
        text = await tr("ACESS_ERR", "en")
        return await bot.send_message(text=text, chat_id=m.chat.id)
    else:
        if m.caption.startswith("/sendto"):
            photo = m.photo[-1]
            photo_id = photo.file_id
            text = m.caption.split(maxsplit=2)
            user = await db.fetchone(
                "SELECT tg_user_id FROM users WHERE tg_user_id=%s OR username=%s",
                (
                    text[1],
                    text[1].lstrip("@"),
                ),
            )
            if len(text) == 3:
                arg = text[2]
                await bot.send_photo(user["tg_user_id"], photo=photo_id, caption=arg)
            else:
                await bot.send_photo(user["tg_user_id"], photo=photo_id)
        elif m.caption.startswith("/reply"):
            photo = m.photo[-1]
            photo_id = photo.file_id
            text = m.caption.split(maxsplit=2)
            user = await db.fetchone(
                "SELECT tg_user_id FROM users WHERE tg_user_id=%s OR username=%s",
                (
                    text[1],
                    text[1].lstrip("@"),
                ),
            )
            arg = int(text[2])
            try:
                await bot.send_photo(
                    user["tg_user_id"], photo=photo_id, reply_to_message_id=arg
                )
            except Exception:
                await bot.send_photo(user["tg_user_id"], photo=photo_id)


@bot.message_handler(
    content_types=["photo"],
    func=lambda m: all(
        (
            m.reply_to_message,
            m.reply_to_message.content_type == "text",
            len(m.reply_to_message.text.split()) == 2,
        )
    ),
)
async def check_save(m):
    print(m)
    print(m.text)


@bot.message_handler(commands=["give"])
async def give(m):
    u = await db.fetchone(
        "SELECT id, admin_lvl, locale FROM users WHERE tg_user_id=%s", (m.from_user.id,)
    )
    if not u or u["admin_lvl"] < 1:
        text = await tr("ACESS_ERR", "en")
        return await bot.send_message(text=text, chat_id=m.chat.id)
    else:
        row = m.text.split()[1:]
        command, user, arg = row[0], row[1], row[2:]
        user = await db.fetchone(
            "SELECT id, username, first_name, tg_user_id FROM users WHERE tg_user_id=%s OR username=%s",
            (user, user.lstrip("@")),
        )
        if user:
            if command == "key":
                count, server = arg[0], arg[1]
                time = arg[2] if len(arg) > 2 else 1
                for _ in range(int(count)):
                    cfg_id = await gen_key(time, user, server)
                    cfg = await db.fetchone(
                        "SELECT c.code_name, u.first_name, u.id FROM configs c JOIN users u ON c.user_id = u.id WHERE c.id=%s",
                        (cfg_id,),
                    )
                    await bot.send_message(
                        ADMIN,
                        f"generate code {cfg['code_name']} for {cfg['first_name']}({cfg['id']})",
                    )
            elif command == "balance":
                count = arg[0]
                await db.execute(
                    "UPDATE users SET balance = balance + %s WHERE id=%s",
                    (int(count), user["id"]),
                )


@bot.message_handler(chat_types=["private"], content_types=["text"])
async def message_hand(m):
    u = await db.fetchone(
        "SELECT id, first_name, locale, admin_lvl, tg_user_id, referal FROM users WHERE tg_user_id=%s",
        (m.from_user.id,),
    )
    if not u:
        text = await tr("NOT_USER", "en")
        return await bot.reply_to(text=text, message=m)
    elif u["id"] in conf_changes.keys():
        if conf_changes[u["id"]].split("_")[0] == "name":
            config_name = m.text
            if len(m.text) <= 32:
                cfg_id = conf_changes[u["id"]].split("_")[1]
                cfg = await db.fetchone(
                    "SELECT name, code_name FROM configs WHERE id=%s", (cfg_id,)
                )
                keyboard = BMarkup(
                    keyboard=[
                        [
                            BButton(
                                text=await tr("YES", u["locale"]),
                                callback_data=f"change_name_{cfg_id}",
                            )
                        ],
                        [
                            BButton(
                                text=await tr("CANCEL", u["locale"]),
                                callback_data="delete_mess",
                            )
                        ],
                    ],
                    row_width=2,
                )
                conf_changes[u["id"]] = config_name
                name = (
                    cfg["name"]
                    if cfg["name"]
                    else "".join(cfg["code_name"].split("_")[1:])
                )
                text = (await tr("CHANGING_CONFIG_NAME", u["locale"])).format(
                    old_name=name, new_name=m.text
                )
                await bot.send_message(
                    text=text, chat_id=m.chat.id, reply_markup=keyboard
                )
            else:
                text = await tr("TOO_LONG_NAME", u["locale"])
                await bot.send_message(text=text, chat_id=m.chat.id)
        elif conf_changes[u["id"]].split("_")[0] == "desc":
            config_desc = m.text
            if len(m.text) <= 255:
                cfg_id = conf_changes[u["id"]].split("_")[1]
                cfg = await db.fetchone(
                    "SELECT description FROM configs WHERE id=%s", (cfg_id,)
                )
                keyboard = BMarkup(
                    keyboard=[
                        [
                            BButton(
                                text=await tr("YES", u["locale"]),
                                callback_data=f"change_descript_{cfg_id}",
                            )
                        ],
                        [
                            BButton(
                                text=await tr("CANCEL", u["locale"]),
                                callback_data="delete_mess",
                            )
                        ],
                    ]
                )
                conf_changes[u["id"]] = config_desc
                if cfg["description"]:
                    text = (await tr("CHANGING_CONFIG_DESC", u["locale"])).format(
                        old_desc=cfg["description"], new_desc=config_desc
                    )
                    await bot.send_message(
                        text=text, chat_id=m.chat.id, reply_markup=keyboard
                    )
                else:
                    text = (await tr("SET_CONFIG_DESC", u["locale"])).format(
                        new_desc=config_desc
                    )
                    await bot.send_message(m.chat.id, text, reply_markup=keyboard)
            else:
                text = await tr("TOO_LONG_DESC", u["locale"])
                await bot.send_message(m.chat.id, text)
    elif u["id"] in balance_depos:
        try:
            summ = int(m.text)
        except Exception:
            text = await tr("SEND_INT", u["locale"])
            return await bot.send_message(text=text, chat_id=m.chat.id)
        if summ < 80:
            text = (await tr("MIN_AMOUNT", u["locale"])).format(min=80)
            return await bot.send_message(text=text, chat_id=m.chat.id)
        price = [
            types.LabeledPrice(
                label=f"Balance deposit {summ}", amount=int(str(summ) + "00")
            )
        ]
        payment_id = await db.execute(
            "INSERT INTO payments (user_id, amount, currency, description) VALUES (%s, %s, %s, %s)",
            (
                u["id"],
                summ,
                "RUB",
                description
                := f"Пополнение внутреннего баланса {u['first_name']}({u['tg_user_id']}) на {summ}руб для оплаты цифровых услуг",
            ),
        )
        pay_operations[f"balance_deposit_{summ}_{payment_id}"] = ""
        await bot.send_invoice(
            chat_id=m.chat.id,
            title=(await tr("INVOICE_DEPOSIT_TITLE", u["locale"])).format(
                amount=summ, name=u["first_name"]
            ),
            description=(await tr("INVOICE_DEPOSIT_DESC", u["locale"])).format(
                amount=summ, name=u["first_name"], id=u["tg_user_id"]
            ),
            invoice_payload=f"balance_deposit_{summ}_{payment_id}",
            provider_token=PROVIDER_TOKEN,
            currency="RUB",
            prices=price,
            photo_url="https://vpw.kirian.su/photos/coin.png",
            need_email=True,
            send_email_to_provider=True,
            provider_data=json.dumps(
                {
                    "receipt": {
                        "items": [
                            {
                                "description": description,
                                "quantity": 1,
                                "amount": {"value": summ, "currency": "RUB"},
                                "vat_code": 1,
                                "payment_mode": "full_payment",
                                "payment_subject": "service",
                            }
                        ]
                    }
                }
            ),
        )
    elif u["id"] in referals:
        if u["referal"]:
            text = await tr("ALREADY_REFERAL", u["locale"])
            return await bot.send_message(text=text, chat_id=m.chat.id)
        code = m.text.strip().split()[0]
        user = await db.fetchone(
            "SELECT id, first_name FROM users WHERE referal_code=%s", (code,)
        )
        if user and user["id"] and not u["referal"] and code != "site":
            await db.execute("UPDATE users SET referal=%s WHERE id=%s", (code, u["id"]))
            text = (await tr("REFERAL_BECAME", u["locale"])).format(
                user=user["first_name"]
            )
        else:
            text = await tr("REFERAL_ERR", u["locale"])
        await bot.send_message(text=text, chat_id=m.chat.id)


@bot.pre_checkout_query_handler(func=lambda query: True)
async def pre_checkout(q):
    u = await db.fetchone("SELECT id FROM users WHERE tg_user_id=%s", (q.from_user.id,))
    if q.invoice_payload in pay_operations.keys():
        if q.invoice_payload.startswith("newconfig"):
            await bot.answer_pre_checkout_query(q.id, ok=True)
        elif q.invoice_payload.startswith("config_extend"):
            await bot.answer_pre_checkout_query(q.id, ok=True)
            pay_operations[q.invoice_payload] = await db.execute(
                "INSERT INTO payments (user_id, config_id, amount, currency, description) VALUES (%s, %s, %s, %s, %s)",
                (
                    u["id"],
                    q.invoice_payload.split("_")[-1],
                    q.total_amount,
                    q.currency,
                    q.invoice_payload,
                ),
            )
        elif q.invoice_payload.startswith("balance"):
            await bot.answer_pre_checkout_query(q.id, ok=True)
    else:
        err = await tr("PRECHECKOUT_ERROR", "en")
        await bot.answer_pre_checkout_query(q.id, ok=False, error_message=err)


@bot.message_handler(content_types=["successful_payment"])
async def successful_payment(m):
    u = await db.fetchone(
        "SELECT id, locale, username, first_name, tg_user_id FROM users WHERE tg_user_id=%s",
        (m.from_user.id,),
    )
    payment = m.successful_payment
    if payment.invoice_payload.startswith("balance"):
        summ = payment.invoice_payload.split("_")[-2]
        del pay_operations[payment.invoice_payload]
        await db.execute(
            "UPDATE payments SET status=%s, paid_at = CURRENT_TIMESTAMP(), raw_payload=%s, provider_tx_id=%s, telegram_tx_id=%s WHERE id=%s",
            (
                "paid",
                json.dumps(m.json, ensure_ascii=False),
                payment.provider_payment_charge_id,
                payment.telegram_payment_charge_id,
                payment.invoice_payload.split("_")[-1],
            ),
        )
        await db.execute(
            "UPDATE users SET balance = balance + %s WHERE tg_user_id=%s",
            (int(summ), m.from_user.id),
        )
        text = (await tr("BALANCE_DEPOSIT_SUCCESS", u["locale"])).format(amount=summ)
        messag = await bot.send_message(text=text, chat_id=m.chat.id)
        await bot.send_message(
            ADMIN,
            f"Пополнение внутреннего баланса {u['first_name']}({u['tg_user_id']}) на {summ}руб для оплаты цифровых услуг",
        )
        await bot.send_message(ADMIN, f"/reply {u['tg_user_id']} {messag.id}")


@bot.callback_query_handler(
    func=lambda c: any(
        c.data.startswith(i)
        for i in [
            "soon",
            "menu",
            "config",
            "extend",
            "buy",
            "pay",
            "accept",
            "delete_mess",
            "change",
            "show",
            "baldeposit",
            "account",
            "referal",
            "choose",
            "set",
            "cancel",
            "help",
            "cfgs",
            "a",
            "p",
        ]
    )
)
async def callback_query(c):
    u = await db.fetchone(
        "SELECT id, username, first_name, admin_lvl, locale, balance, configs_count FROM users WHERE tg_user_id=%s",
        (c.from_user.id,),
    )
    cfg = None
    if not u:
        text = await tr("NOT_USER", "en")
        return await bot.answer_callback_query(callback_query_id=c.id, text=text)
    if c.data.startswith("soon"):
        text = await tr("SOON_FUNC", u["locale"])
        return await bot.answer_callback_query(
            text=text, callback_query_id=c.id, show_alert=True
        )

    # Input from send_welcome() / BButton("back")
    elif c.data.startswith("menu_main"):
        keyboard = BMarkup()
        keyboard.row(
            BButton(text=await tr("MY_CFGS", u["locale"]), callback_data="menu_cfg")
        )
        keyboard.row(
            BButton(
                text=await tr("FREE_PRESENT", u["locale"]),
                callback_data="choose_location_free",
            )
        )
        keyboard.row(
            BButton(text=await tr("ACCOUNT", u["locale"]), callback_data="menu_account")
        )
        keyboard.row(
            BButton(
                text=await tr("INFO", u["locale"]), callback_data="menu_information"
            )
        )
        keyboard.row(
            BButton(
                text=await tr("BUY_CFG", u["locale"]),
                callback_data="choose_location_buy",
            )
        )
        keyboard.row(
            BButton(text=await tr("DEPOSIT", u["locale"]), callback_data="baldeposit")
        )
        keyboard.row(
            BButton(
                text=await tr("LANG_CHANGE", u["locale"]),
                callback_data="choose_language",
            )
        )
        text = (await tr("MENU_MESS", u["locale"])).format(
            balance=u["balance"], count=u["configs_count"]
        )
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output menu_cfg / menu_account / menu_information / choose_location_buy / baldeposit / choose_language

    # Input from menu_main
    elif c.data.startswith("menu_cfg"):
        rows = await db.fetchall(
            "SELECT id, name, code_name FROM configs WHERE user_id=%s and status='active'",
            (u["id"],),
        )
        if not (rows):
            keyboard = BMarkup(
                keyboard=[
                    [
                        BButton(
                            text=await tr("BACK", u["locale"]),
                            callback_data="menu_main",
                        )
                    ]
                ]
            )
            text = await tr("NO_CONFIGS", u["locale"])
            return await bot.edit_message_text(
                text=text,
                chat_id=c.message.chat.id,
                message_id=c.message.id,
                reply_markup=keyboard,
            )
        buttons = [
            BButton(
                text=(
                    i["name"] if i["name"] else "".join(i["code_name"].split("_")[1:])
                ),
                callback_data=f"config_menu_{i['id']}",
            )
            for i in rows
        ]
        # buttons.append(BButton(text=await tr("CONFIGS_EXTEND", u['locale']), callback_data="configs_extend"))
        keyboard = BMarkup(
            row_width=int(int(len(buttons)) / 8)
            if int(len(buttons)) / 8 == len(buttons)
            else (int(int(len(buttons)) / 8) + 1)
        )
        keyboard.add(*buttons)
        keyboard.row(
            BButton(
                text=await tr("CONFIGS_EXTEND", u["locale"]),
                callback_data="cfgs:extnd",
            )
        )
        keyboard.row(
            BButton(text=await tr("BACK", u["locale"]), callback_data="menu_main")
        )
        text = await tr("CHOOSE_CONFIG", u["locale"])
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output config_menu_(config id)

    # Input from menu_main
    elif c.data.startswith("choose_language"):
        buttons = [
            BButton(text="🇷🇺Русский(RU)", callback_data="set_language_ru"),
            BButton(text="🇬🇧English(UK)", callback_data="set_language_en"),
            BButton(text=await tr("BACK", u["locale"]), callback_data="menu_main"),
        ]
        keyboard = BMarkup(row_width=1)
        keyboard.add(*buttons)
        text = "Choose language / Выберите язык"
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output set_language_(ru/en)

    # Input _(ru/en) from choose_language
    elif c.data.startswith("set_language_"):
        lang = c.data.split("_")[-1]
        await db.execute("UPDATE users SET locale=%s WHERE id=%s", (lang, u["id"]))
        text = await tr("LANG_SET_SUCCESS", lang)
        keyboard = BMarkup(
            keyboard=[[BButton(text=await tr("BACK", lang), callback_data="menu_main")]]
        )
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output Message

    # Input _(config id)
    elif c.data.startswith("config_menu_"):
        cfg_id = c.data.split("_")[-1]
        cfg = await db.fetchone(
            "SELECT name, code_name, valid_until, description FROM configs WHERE id=%s",
            (cfg_id,),
        )
        name = "".join(
            (cfg["name"] if cfg["name"] else cfg["code_name"].split("_")[1:])
        )
        description = cfg["description"] or "-"
        keyboard = BMarkup(
            keyboard=[
                [
                    BButton(
                        text=await tr("BTN_SHOW_QR", u["locale"]),
                        callback_data=f"show_config_qr_{cfg_id}",
                    )
                ],
                [
                    BButton(
                        text=await tr("BTN_GET_FILE", u["locale"]),
                        callback_data=f"show_config_conf_{cfg_id}",
                    )
                ],
                [
                    BButton(
                        text=await tr("BTN_CONFIG_RESET", u["locale"]),
                        callback_data=f"config_reset_{cfg_id}",
                    )
                ],
                [
                    BButton(
                        text=await tr("BTN_EXTEND_CONFIG", u["locale"]),
                        callback_data=f"extend_config_{cfg_id}",
                    )
                ],
                [
                    BButton(
                        text=await tr("BTN_EDIT_CONFIG", u["locale"]),
                        callback_data=f"config_settings_{cfg_id}",
                    )
                ],
                [
                    BButton(
                        text=await tr("BTN_CHANGE_LOCATION", u["locale"]),
                        callback_data=f"config_location_{cfg_id}",
                    )
                ],
                [BButton(text=await tr("BACK", u["locale"]), callback_data="menu_cfg")],
            ],
            row_width=1,
        )
        text = "<code>"
        with open(os.path.join(CONF_DIR, str(cfg["code_name"]) + ".txt"), "r") as f:
            text += f.readline()
        text += "</code>\n\n(сверху ключ для подключения конфига через вставку текста, копируется нажатием на него, это тут временно, потом придумаю куда его убрать)\n\n"
        text += (await tr("CONFIG_MENU", u["locale"])).format(
            name=name, valid_until=cfg["valid_until"], description=description
        )
        if c.message.content_type in ["photo", "document"]:
            try:
                await bot.delete_message(
                    chat_id=c.message.chat.id, message_id=c.message.id
                )
            except Exception:
                pass
            return await bot.send_message(
                text=text, chat_id=c.message.chat.id, reply_markup=keyboard
            )
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output show_config_qr_(config id) / show_config_conf_(config id) / extend_config_(config id) / config_settings_(config id) / menu_cfg

    # Input _(config id)
    elif c.data.startswith("config_reset_"):
        cfg = await db.fetchone(
            "SELECT c.name, c.code_name, c.user_id, l.host, l.key_path, l.directory FROM configs c JOIN locations l ON c.location_id = l.id WHERE c.id=%s",
            (c.data.split("_")[-1],),
        )
        await ssh.reset_key(
            host=cfg["host"],
            ssh_key=cfg["key_path"],
            directory=cfg["directory"],
            cfg_name=cfg["code_name"],
        )
        if cfg["host"] not in ("localhost", "127.0.0.0", "127.0.0.1"):
            await ssh.get_key(
                host=cfg["host"],
                ssh_key=cfg["key_path"],
                directory=cfg["directory"],
                cfg_name=cfg["code_name"],
            )
        text = await tr("CONFIG_RESET_SUCCESS", u["locale"])
        await config_help(c.message, text, cfg["code_name"], cfg["name"])

    # Input _(config id)
    elif c.data.startswith("config_location_"):
        cfg_id = c.data.split("_")[-1]
        cfg = await db.fetchone(
            "SELECT name, code_name, location_id FROM configs WHERE id=%s", (cfg_id,)
        )
        keyboard = BMarkup(row_width=2)
        buttons = [
            BButton(
                text=i["name"],
                callback_data=f"change_config_location_{cfg_id}_{i['id']}",
            )
            for i in await db.fetchall(
                "SELECT id, name FROM locations WHERE is_active = 1 AND id != %s",
                (cfg["location_id"],),
            )
        ]
        buttons.append(
            BButton(
                text=await tr("BACK", u["locale"]),
                callback_data=f"config_menu_{cfg_id}",
            )
        )
        keyboard.add(*buttons)
        text = (await tr("CHOOSE_NEW_LOCATION", u["locale"])).format(
            name=cfg["name"]
            if cfg["name"]
            else "".join(cfg["code_name"].split("_")[1:])
        )
        return await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output change_config_location_(config code_name)_(location id)

    # Input _(code_name)_(location id)
    elif c.data.startswith("change_config_location_"):
        cfg_id, loc_id = c.data.split("_")[-2:]
        await bot.answer_callback_query(callback_query_id=c.id)
        await bot.edit_message_text(
            text=await tr("CONFIG_LOCATION_CHANGING", u["locale"]),
            chat_id=c.message.chat.id,
            message_id=c.message.id,
        )
        cfg = await db.fetchone(
            "SELECT c.id, c.name, c.code_name, c.location_id, l.host, l.key_path, l.directory FROM configs c JOIN locations l ON c.location_id=l.id WHERE c.id=%s",
            (cfg_id,),
        )
        loc = await db.fetchone(
            "SELECT id, name, host, key_path, directory FROM locations WHERE id=%s",
            (loc_id,),
        )
        if cfg["location_id"] == int(loc_id):
            return await bot.edit_message_text(
                text="ERROR AE34", chat_id=c.message.chat.id, message_id=c.message.id
            )
        await ssh.del_key(
            host=cfg["host"],
            ssh_key=cfg["key_path"],
            directory=cfg["directory"],
            cfg_name=cfg["code_name"],
        )
        code_name = f"{loc['name']}_{'_'.join(cfg['code_name'].split('_')[1:])}"
        await ssh.new_key(
            host=loc["host"],
            ssh_key=loc["key_path"],
            directory=loc["directory"],
            cfg_name=code_name,
        )
        await db.execute(
            "UPDATE configs SET location_id=%s, code_name=%s WHERE id = %s",
            (loc_id, code_name, cfg["id"]),
        )
        if loc["host"] not in ("localhost", "127.0.0.0", "127.0.0.1"):
            await ssh.get_key(loc["host"], loc["key_path"], loc["directory"], code_name)
        text = (await tr("CONFIG_LOCATION_CHANGED", u["locale"])).format(
            location=loc["name"],
            name=cfg["name"] if cfg["name"] else "".join(code_name.split("_")[1:]),
        )
        await bot.delete_message(chat_id=c.message.chat.id, message_id=c.message.id)
        await config_help(c.message, text, code_name, cfg["name"])

    # Input choose_location_(type)
    elif c.data.startswith("choose_location_"):
        type = c.data.split("_")[2]
        locations = await db.fetchall(
            "SELECT id, name FROM locations WHERE is_active = 1"
        )
        keyboard = BMarkup(row_width=2)
        buttons = [
            BButton(text=i["name"], callback_data=f"choose_tariff_{type}_{i['id']}")
            for i in locations
        ]
        if type == "free":
            buttons = [
                BButton(text=i["name"], callback_data=f"config_free_{i['id']}")
                for i in locations
            ]
        buttons.append(
            BButton(text=await tr("BTN_SOON", u["locale"]), callback_data="soon")
        )
        keyboard.add(*buttons)
        keyboard.row(
            BButton(text=await tr("BACK", u["locale"]), callback_data="menu_main")
        )
        text = await tr("CHOOSE_LOCATION", u["locale"])
        return await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output choose_tariff_(type)_(location id)

    # Input _(type)_(location id/config id)
    elif c.data.startswith("choose_tariff_"):
        cfg = None
        type, loc_id = c.data.split("_")[2:]
        if type == "buy":
            # buttons = [
            #    BButton(text=f"{x}{await tr("MO", u['locale'])}({await price_counter(x)}{await tr("RUB", u['locale'])})", callback_data=f"choose_pay_buy_{loc_id}_{x}")
            #    for x in tariff_multip.keys()
            # ]
            buttons = [
                BButton(
                    text=f"{x}{await tr('MO', u['locale'])}({await price_counter(x)}{await tr('RUB', u['locale'])})",
                    callback_data=f"pay_config_{loc_id}_{x}",
                )
                for x in tariff_multip.keys()
            ]
        if type == "extend":
            cfg = await db.fetchone(
                "SELECT price FROM configs WHERE id = %s", (loc_id,)
            )
            if cfg and cfg["price"] < 80:
                # buttons = [
                #    BButton(text=f"{x}{await tr("MO", u['locale'])}({await price_counter(x)}{await tr("RUB", u['locale'])})", callback_data=f"choose_pay_extend_{loc_id}_{x}")
                #    for x in tariff_multip.keys()
                # ]
                buttons = [
                    BButton(
                        text=f"{x}{await tr('MO', u['locale'])}({await price_counter(x)}{await tr('RUB', u['locale'])})",
                        callback_data=f"pay_extend_config_{loc_id}_{x}",
                    )
                    for x in tariff_multip.keys()
                ]
        keyboard = BMarkup(row_width=2)
        keyboard.add(*buttons)
        if type == "buy":
            keyboard.row(
                BButton(
                    text=await tr("BACK", u["locale"]),
                    callback_data=f"choose_location_{type}",
                )
            )
        text = await tr("CFG_DURATION", u["locale"])
        return await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output choose_pay_(buy/extend)_(location id/config id)_(tariff key) / cheese_location_(type)

    # Input _(type)_(location id/config id)_(tariff key)
    elif c.data.startswith("choose_pay_"):
        type, loc_id, tariff_k = c.data.split("_")[2:]
        tariff_k = int(tariff_k)
        if type == "buy":
            buttons = [
                # BButton(text="ЮKassa", callback_data=f"buy_config_{loc_id}_{tariff_k}"),
                BButton(
                    text=await tr("BALANCE_PAY", u["locale"]),
                    callback_data=f"pay_config_{loc_id}_{tariff_k}",
                )
            ]
        elif type == "extend":
            buttons = [
                # BButton(text="ЮKassa", callback_data=f"buy_extend_config_{loc_id}_{tariff_k}"),
                BButton(
                    text=await tr("BALANCE_PAY", u["locale"]),
                    callback_data=f"pay_extend_config_{loc_id}_{tariff_k}",
                )
            ]
            cfg = await db.fetchone(
                "SELECT price FROM configs WHERE id = %s", (loc_id,)
            )
            if cfg["price"] < 80:
                buttons = [
                    BButton(
                        text=await tr("BALANCE", u["locale"]),
                        callback_data=f"pay_extend_config_{loc_id}_{tariff_k}",
                    )
                ]
        keyboard = BMarkup(row_width=2)
        keyboard.add(*buttons)
        keyboard.row(
            BButton(
                text=await tr("BACK", u["locale"]),
                callback_data=f"choose_tariff_{type}_{loc_id}",
            )
        )
        amount = (
            await price_counter(tariff_k, cfg["price"])
            if cfg
            else await price_counter(tariff_k)
        )
        text = (await tr("PAY_SUMMARY", u["locale"])).format(
            amount=amount, balance=u["balance"]
        )
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output buy_config_(location id)_(tariff_k) / pay_config_(location id)_(tariff_k) / buy_extend_config_(config id)_(tariff k) / pay_extend_config_(config id)_(tariff_k)

    # Input _(location id)_(tariff key)
    elif c.data.startswith("pay_config_"):
        loc_id, tariff_k = c.data.split("_")[2], int(c.data.split("_")[3])
        summ = await price_counter(tariff_k)
        if u["balance"] >= summ:
            text = (await tr("PAY_FROM_BALANCE", u["locale"])).format(
                amount=summ, balance=u["balance"]
            )
            keyboard = BMarkup(row_width=2)
            buttons = [
                BButton(
                    text=await tr("Оплатить", u["locale"]),
                    callback_data=f"accept_pay_config_{loc_id}_{summ}_{tariff_k}",
                ),
                BButton(
                    text=await tr("Отмена", u["locale"]), callback_data="delete_mess"
                ),
            ]
            keyboard.add(*buttons)
            await bot.edit_message_text(
                text=text,
                chat_id=c.message.chat.id,
                message_id=c.message.id,
                reply_markup=keyboard,
            )
        else:
            text = await tr("INSUFFICIENT_FUNDS", u["locale"])
            keyboard = BMarkup(
                keyboard=[
                    [
                        BButton(
                            text=await tr("DEPOSIT", u["locale"]),
                            callback_data="baldeposit",
                        )
                    ],
                    [
                        BButton(
                            text=await tr("BACK", u["locale"]),
                            callback_data="menu_main",
                        )
                    ],
                ]
            )
            await bot.edit_message_text(
                text=text,
                chat_id=c.message.chat.id,
                message_id=c.message.id,
                reply_markup=keyboard,
            )
    # Output accept_pay_config_(location id)_(summ) / delete_mess

    # Input _(location id)_(summ)_(tariff key)
    elif c.data.startswith("accept_pay_config_"):
        loc_id, summ, tariff_k = c.data.split("_")[3:]
        tariff_k = int(tariff_k)
        try:
            await bot.delete_message(chat_id=c.message.chat.id, message_id=c.message.id)
        except Exception:
            pass
        if u["balance"] >= (summ := int(summ)):
            await db.execute(
                "UPDATE users SET balance = balance - %s WHERE id = %s AND balance >= %s",
                (summ, u["id"], summ),
            )
            cfg_id = await gen_key(tariff_k, u, loc_id)
            cfg = await db.fetchone(
                "SELECT code_name, name FROM configs WHERE id = %s", (cfg_id,)
            )
            text = await tr("CONFIG_HELP", u["locale"])
            await config_help(c.message.chat.id, text, cfg["code_name"])
    # Output Message(config_help, qr code, document)

    # Input _(config id)
    elif c.data.startswith("extend_config_"):
        cfg_id = int(c.data.split("_")[2])
        cfg = await db.fetchone("SELECT price FROM configs WHERE id = %s", (cfg_id,))
        if cfg["price"]:
            buttons = [
                BButton(
                    text=f"{x}{await tr('MO', u['locale'])}({await price_counter(x, cfg['price'])}{await tr('RUB', u['locale'])})",
                    callback_data=f"pay_extend_config_{cfg_id}_{x}",
                )
                for x in tariff_multip.keys()
            ]
        else:
            buttons = [
                BButton(
                    text=f"{x}{await tr('MO', u['locale'])}({await price_counter(x)}{await tr('RUB', u['locale'])})",
                    callback_data=f"pay_extend_config_{cfg_id}_{x}",
                )
                for x in tariff_multip.keys()
            ]
        buttons.append(
            BButton(text=await tr("BTN_SOON", u["locale"]), callback_data="soon")
        )
        keyboard = BMarkup(row_width=2)
        keyboard.add(*buttons)
        keyboard.row(
            BButton(
                text=await tr("BACK", u["locale"]),
                callback_data="config_menu_" + str(cfg_id),
            )
        )
        text = await tr("CHOOSE_CONFIG_TARIFF", u["locale"])
        return await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output buy_extend_config_(config id)_(tariff key)

    # Input pay_extend_config_(config id)_(tariff key)
    elif c.data.startswith("pay_extend_config_"):
        cfg_id, tariff_k = list(map(int, c.data.split("_")[3:]))
        summ = await price_counter(tariff_k, base_price)
        cfg = await db.fetchone("SELECT price FROM configs WHERE id = %s", (cfg_id,))
        if cfg["price"]:
            summ = await price_counter(tariff_k, cfg["price"])
        if u["balance"] >= summ:
            text = (await tr("PAY_FROM_BALANCE", u["locale"])).format(
                amount=summ, balance=u["balance"]
            )
            keyboard = BMarkup(row_width=2)
            buttons = [
                BButton(
                    text=await tr("Оплатить", u["locale"]),
                    callback_data=f"accept_pay_extend_{cfg_id}_{summ}_{tariff_k}",
                ),
                BButton(
                    text=await tr("Отмена", u["locale"]), callback_data="delete_mess"
                ),
            ]
            keyboard.add(*buttons)
            await bot.edit_message_text(
                text=text,
                chat_id=c.message.chat.id,
                message_id=c.message.id,
                reply_markup=keyboard,
            )
    # Output accept_pay_extend_(config id)_(summ)_(tariff key) / delete_mess

    # Input _(config id)_(summ)_(tariff key)
    elif c.data.startswith("accept_pay_extend_"):
        try:
            await bot.delete_message(c.message.chat.id, c.message.id)
        except Exception:
            pass
        cfg_id, summ, tariff_k = list(map(int, c.data.split("_")[3:]))
        if u["balance"] >= (summ := int(summ)):
            amount, unit = await to_msql(tariff_k)
            await db.execute(
                "UPDATE users SET balance = balance - %s WHERE id = %s AND balance >= %s",
                (summ, u["id"], summ),
            )
            await db.execute(
                "UPDATE configs SET valid_until=TIMESTAMPADD("
                + unit
                + ", %s, valid_until) WHERE id=%s",
                (amount, cfg_id),
            )
            cfg = await db.fetchone(
                "SELECT code_name, name FROM configs WHERE id=%s", (cfg_id,)
            )
            name = (
                cfg["name"] if cfg["name"] else "".join(cfg["code_name"].split("_")[1:])
            )
            text = (await tr("CONFIG_EXTEND_SUCCESS", u["locale"])).format(name=name)
            await bot.send_message(text=text, chat_id=c.message.chat.id)

    # Input _(config id) from cofig_menu / show_config_qr
    elif c.data.startswith("show_config_conf_"):
        try:
            await bot.delete_message(c.message.chat.id, c.message.id)
        except Exception:
            pass
        cfg_id = c.data.split("_")[-1]
        cfg = await db.fetchone(
            "SELECT name, code_name, location_id, valid_until FROM configs WHERE id = %s",
            (cfg_id,),
        )
        if cfg["location_id"] != 1:
            location = await db.fetchone(
                "SELECT host, key_path, directory FROM locations WHERE id = %s",
                (cfg["location_id"],),
            )
            await ssh.get_conf(
                location["host"],
                location["key_path"],
                location["directory"],
                cfg["code_name"],
            )
        name = "".join(cfg["name"] if cfg["name"] else cfg["code_name"].split("_")[1:])
        keyboard = BMarkup(
            keyboard=[
                [
                    BButton(
                        text=await tr("BTN_SHOW_QR", u["locale"]),
                        callback_data=f"show_config_qr_{cfg_id}",
                    )
                ],
                [
                    BButton(
                        text=await tr("BACK", u["locale"]),
                        callback_data=f"config_menu_{cfg_id}",
                    )
                ],
            ]
        )
        with open(os.path.join(CONF_DIR, cfg["code_name"] + ".conf"), "rb") as file:
            caption = (await tr("CONFIG_VALID_UNTIL", u["locale"])).format(
                date=cfg["valid_until"]
            )
            await bot.send_document(
                chat_id=c.message.chat.id,
                document=types.InputFile(file, file_name=name + ".conf"),
                caption=caption,
                reply_markup=keyboard,
            )
    # Output Message(document) , show_config_qr_(config id) / config_menu_(config id)

    # Input _(config id) from cofig_menu / show_config_conf
    elif c.data.startswith("show_config_qr_"):
        try:
            await bot.delete_message(c.message.chat.id, c.message.id)
        except Exception:
            pass
        cfg_id = c.data.split("_")[-1]
        cfg = await db.fetchone(
            "SELECT name, code_name, location_id, valid_until FROM configs WHERE id = %s",
            (cfg_id,),
        )
        if cfg["location_id"] != 1:
            location = await db.fetchone(
                "SELECT host, key_path, directory FROM locations WHERE id = %s",
                (cfg["location_id"],),
            )
            await ssh.get_qr(
                location["host"],
                location["key_path"],
                location["directory"],
                cfg["code_name"],
            )
        name = "".join(
            (cfg["name"] if cfg["name"] else cfg["code_name"]).split("_")[1:]
        )
        keyboard = BMarkup(
            keyboard=[
                [
                    BButton(
                        text=await tr("BTN_GET_FILE", u["locale"]),
                        callback_data=f"show_config_conf_{cfg_id}",
                    )
                ],
                [
                    BButton(
                        text=await tr("BACK", u["locale"]),
                        callback_data=f"config_menu_{cfg_id}",
                    )
                ],
            ]
        )
        caption = (await tr("CONFIG_VALID_UNTIL", u["locale"])).format(
            date=cfg["valid_until"]
        )
        with open(os.path.join(CONF_DIR, cfg["code_name"] + ".png"), "rb") as qr:
            await bot.send_photo(
                chat_id=c.message.chat.id,
                photo=qr,
                caption=f"{name} {caption}",
                reply_markup=keyboard,
            )
    # Output Message(photo) , show_config_conf_(config id) / config_menu_(config id)

    # Input _(config id) from config_menu
    elif c.data.startswith("config_settings_"):
        cfg_id = c.data.split("_")[-1]
        conf_changes[u["id"]] = cfg_id
        cfg = await db.fetchone(
            "SELECT name, code_name FROM configs WHERE id=%s", (cfg_id,)
        )
        name = cfg["name"] if cfg["name"] else "".join(cfg["code_name"].split("_")[1:])
        keyboard = BMarkup(
            keyboard=[
                [BButton(text="Название", callback_data=f"config_name_{cfg_id}")],
                [BButton(text="Описание", callback_data=f"config_descript_{cfg_id}")],
                [
                    BButton(
                        text=await tr("BACK", u["locale"]),
                        callback_data=f"config_menu_{cfg_id}",
                    )
                ],
            ]
        )
        text = (await tr("CONFIG_SETTINGS_PROMPT", u["locale"])).format(config=name)
        return await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output config_name_(config id) / config_descript_(config id) ; conf_changes[u[id]] = (config id) / config_menu_(config id)

    # Input _(config id)
    elif c.data.startswith("config_name_"):
        cfg_id = c.data.split("_")[-1]
        conf_changes[u["id"]] = f"name_{cfg_id}"
        cfg = await db.fetchone(
            "SELECT name, code_name FROM configs WHERE id=%s", (cfg_id,)
        )
        name = "".join(
            (cfg["name"] if cfg["name"] else cfg["code_name"].split("_")[1:])
        )
        text = await tr("ASK_CONFIG_NAME", u["locale"])
        await bot.edit_message_text(
            text=text, chat_id=c.message.chat.id, message_id=c.message.id
        )
    # Output Message, conf_changes[u[id]] := name_(config_id)

    # Input _(config id)
    elif c.data.startswith("config_descript_"):
        cfg_id = c.data.split("_")[-1]
        conf_changes[u["id"]] = f"desc_{cfg_id}"
        cfg = await db.fetchone(
            "SELECT name, code_name FROM configs WHERE id=%s", (cfg_id,)
        )
        name = "".join(
            (cfg["name"] if cfg["name"] else cfg["code_name"].split("_")[1:])
        )
        text = await tr("ASK_CONFIG_DESC", u["locale"])
        await bot.edit_message_text(
            text=text, chat_id=c.message.chat.id, message_id=c.message.id
        )
    # Output Message, conf_changes[u[id]] := desc_(config_id)

    # Input _(config id)
    elif c.data.startswith("change_name_"):
        cfg_id = c.data.split("_")[2]
        text_val = conf_changes[u["id"]]
        cfg = await db.fetchone("SELECT code_name FROM configs WHERE id=%s", (cfg_id,))
        await db.execute(
            "UPDATE configs SET name = %s WHERE id = %s", (text_val, cfg_id)
        )
        msg = (await tr("CONFIG_NAME_CHANGED", u["locale"])).format(
            code_name=cfg["code_name"], text=text_val
        )
        await bot.edit_message_text(
            text=msg, chat_id=c.message.chat.id, message_id=c.message.id
        )
    # Output Message, change name in db

    # Input _(config id)
    elif c.data.startswith("change_descript_"):
        cfg_id = c.data.split("_")[2]
        text_val = conf_changes[u["id"]]
        await db.fetchone("SELECT code_name, name FROM configs WHERE id=%s", (cfg_id,))
        await db.execute(
            "UPDATE configs SET description = %s WHERE id = %s", (text_val, cfg_id)
        )
        msg = (await tr("CONFIG_DESC_CHANGED", u["locale"])).format(text=text_val)
        await bot.edit_message_text(
            text=msg, chat_id=c.message.chat.id, message_id=c.message.id
        )
    # Output Message, change description in db

    # Input
    elif c.data.startswith("baldeposit"):
        balance_depos.append(u["id"])
        keyboard = BMarkup(
            keyboard=[
                [
                    BButton(
                        text=await tr("CANCEL", u["locale"]),
                        callback_data="cancel_deposit",
                    )
                ]
            ]
        )
        text = await tr("ASK_DEPOSIT_SUM", u["locale"])
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output Message, balance_depos.append(u[id]) / cancel_deposit

    # Input
    elif c.data.startswith("cancel_deposit"):
        keyboard = BMarkup(
            keyboard=[
                [BButton(text=await tr("BACK", u["locale"]), callback_data="menu_main")]
            ]
        )
        try:
            balance_depos.remove(u["id"])
        except Exception:
            pass
        text = await tr("DEPOSIT_CANCELED", u["locale"])
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output remove u[id] from balance_depos

    # Input
    elif c.data.startswith("menu_account"):
        keyboard = BMarkup(
            keyboard=[
                [
                    BButton(
                        text=await tr("REFERRAL_PROGRAM", u["locale"]),
                        callback_data="referal_menu",
                    )
                ],
                [
                    BButton(
                        text=await tr("BACK", u["locale"]), callback_data="menu_main"
                    )
                ],
            ]
        )
        text = await tr("ACCOUNT_MENU_TITLE", u["locale"])
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output referal_menu / menu_main

    # Input from menu_account
    elif c.data.startswith("referal_menu"):
        keyboard = BMarkup()
        keyboard.row(
            BButton(
                text=await tr("BTN_MY_REF_CODE", u["locale"]),
                callback_data="referal_get",
            )
        )
        keyboard.row(
            BButton(
                text=await tr("BTN_INPUT_REF_CODE", u["locale"]),
                callback_data="referal_became",
            )
        )
        keyboard.row(
            BButton(text=await tr("BACK", u["locale"]), callback_data="menu_account")
        )
        text = await tr("REFERRAL_MENU_TITLE", u["locale"])
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output referal_get / referal_became / menu_account

    # Input from referal_menu
    elif c.data.startswith("referal_became"):
        referals.append(u["id"])
        text = await tr("REFERRAL_ENTER_CODE", u["locale"])
        await bot.edit_message_text(
            text=text, chat_id=c.message.chat.id, message_id=c.message.id
        )
    # Output referals.append(u[id])

    # Input from referal_menu
    elif c.data.startswith("referal_get"):
        code = (
            await db.fetchone(
                "SELECT referal_code FROM users WHERE id = %s", (u["id"],)
            )
        )["referal_code"]
        keyboard = BMarkup()
        keyboard.row(
            BButton(
                text=await tr("BTN_COPY_CODE", u["locale"]),
                copy_text=types.CopyTextButton(text=code),
            )
        )
        keyboard.row(
            BButton(
                text=await tr("BTN_COPY_LINK", u["locale"]),
                copy_text=types.CopyTextButton(
                    text=f"https://t.me/{(await bot.get_me()).username}?start={code}"
                ),
            )
        )
        keyboard.row(
            BButton(text=await tr("BACK", u["locale"]), callback_data="referal_menu")
        )
        text = (await tr("REF_CODE_TEXT", u["locale"])).format(code=code)
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output Copy_text / referal_menu

    # Input from menu_main
    elif c.data.startswith("menu_information"):
        keyboard = BMarkup()
        keyboard.row(
            BButton(
                text=await tr("BOT_CHANNEL", u["locale"]),
                url="https://t.me/Kirians_dev",
            )
        )
        keyboard.row(
            BButton(text=await tr("BOT_SITE", u["locale"]), url="https://vpw.kirian.su")
        )
        keyboard.row(
            BButton(text=await tr("VPN_HELP", u["locale"]), callback_data="help_vpn")
        )
        keyboard.row(
            BButton(text=await tr("BACK", u["locale"]), callback_data="menu_main")
        )
        text = await tr("BOT_INFO", u["locale"])
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )
    # Output Url / menu_main / help_vpn

    elif c.data.startswith("help_vpn"):
        keyboard = BMarkup()
        keyboard.row(
            BButton(
                text=await tr("BACK", u["locale"]), callback_data="menu_information"
            )
        )
        text = await tr("VPN_HELP_TEXT", u["locale"])
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )

    # Input _(location id)
    elif c.data.startswith("config_free_"):
        loc_id = c.data.split("_")[-1]
        location = await db.fetchone(
            "SELECT id, name, host, key_path, directory FROM locations WHERE id=%s",
            (int(loc_id),),
        )
        # cfg_id = await db.execute("INSERT INTO configs (user_id, location_id) VALUES (%s, %s)",
        #                          (u['id'], int(loc_id)))
        # cfg_name = f"{location['name']}_{c.from_user.username}_{cfg_id}"
        # new_key(host: str, ssh_key: str, directory: str, cfg_name: str)
        # await ssh.new_key(host=location['host'], ssh_key=location['key_path'], directory=location['directory'], cfg_name=cfg_name)
        # if location['id'] != 1:
        #    await ssh.get_key(host=location['host'], ssh_key=location['key_path'], directory=location['directory'], cfg_name=cfg_name)
        # await gen_key(cfg_name, cfg_id, "15min", u)
        # await db.execute("UPDATE configs SET code_name=%s, valid_until=%s, status='active' where id=%s",
        #                 (cfg_name, (str(dt.now()+td(minutes=30)).split("."))[0], cfg_id))
        cfg_id = await gen_key(30, u, loc_id)
        cfg = await db.fetchone(
            "SELECT code_name FROM configs WHERE id = %s", (cfg_id,)
        )
        text = (await tr("FREE_CONFIG_HELP", u["locale"])).format(
            name="".join(cfg["code_name"].split("_")[1:])
        )
        await config_help(c.message, text, cfg["code_name"])
    # Output Message(config_help, qr code, document)

    elif c.data.startswith("cfgs:extnd"):
        ch_cfgs = (
            set((c.data.split(":")[2]).split(","))
            if len(c.data.split(":")) > 2 and c.data.split(":")[2]
            else set()
        )
        cfgs = await db.fetchall(
            "SELECT id, code_name, name, price, valid_until FROM configs WHERE user_id=%s AND status='active'",
            (u["id"],),
        )
        keyboard = BMarkup(row_width=1)
        for cfg in cfgs:
            n_cfgs = ch_cfgs.copy()
            price = cfg["price"] if cfg["price"] else await price_counter(1)
            name = (
                cfg["name"] if cfg["name"] else "".join(cfg["code_name"].split("_")[1:])
            )
            if str(cfg["id"]) in ch_cfgs:
                n_cfgs.remove(str(cfg["id"]))
                keyboard.add(
                    BButton(
                        text=f"✅ {name}({price}{await tr('RUB', u['locale'])}/{await tr('MO', u['locale'])}) ({await tr('VALID_UNTIL', u['locale'])}: {'.'.join(str(str(cfg['valid_until']).split(' ')[0]).split('-')[::-1])})",
                        callback_data=f"cfgs:extnd:{','.join(n_cfgs)}",
                    )
                )
            else:
                n_cfgs.add(str(cfg["id"]))
                keyboard.add(
                    BButton(
                        text=f"❌ {name}({price}{await tr('RUB', u['locale'])}/{await tr('MO', u['locale'])}) ({await tr('VALID_UNTIL', u['locale'])}: {'.'.join(str(str(cfg['valid_until']).split(' ')[0]).split('-')[::-1])})",
                        callback_data=f"cfgs:extnd:{','.join(n_cfgs)}",
                    )
                )
        keyboard.row(
            BButton(
                text=await tr("PROCEED_TO_PAY", u["locale"]),
                callback_data=f"p:cfgs:extnd:{','.join(ch_cfgs)}",
            )
        )
        keyboard.row(
            BButton(text=await tr("BACK", u["locale"]), callback_data="menu_cfgs")
        )
        if len(ch_cfgs) < 6:
            text = await tr("CHOOSE_CONFIGS_TO_EXTEND", u["locale"])
        else:
            text = await tr("CHOOSE_CONFIGS_TO_EXTEND_MANY", u["locale"])
        await bot.edit_message_text(
            text=text,
            chat_id=c.message.chat.id,
            message_id=c.message.id,
            reply_markup=keyboard,
        )

    elif c.data.startswith("p:cfgs:extnd"):
        cfgs = (
            set(c.data.split(":")[3].split(","))
            if len(c.data.split(":")) > 3 and c.data.split(":")[3]
            else set()
        )
        if not cfgs:
            text = await tr("NO_CONFIGS_SELECTED", u["locale"])
            return await bot.answer_callback_query(
                callback_query_id=c.id, text=text, show_alert=True
            )
        else:
            configs = list()
            total_price = 0
            for cfg_id in sorted(list(map(int, cfgs))):
                cfg = await db.fetchone(
                    "SELECT name, code_name, price FROM configs WHERE id=%s", (cfg_id,)
                )
                if cfg and cfg["price"]:
                    total_price += int(cfg["price"])
                    price = cfg["price"]
                else:
                    total_price += await price_counter(1)
                    price = await price_counter(1)
                name = (
                    cfg["name"]
                    if cfg and cfg["name"]
                    else "".join(cfg["code_name"].split("_")[1:])
                )
                configs.append(name + f" ({price}{await tr('RUB', u['locale'])})")
            text = (await tr("PAY_CONFIGS_FROM_BALANCE", u["locale"])).format(
                amount=total_price, balance=u["balance"], name="\n".join(configs)
            )
            keyboard = BMarkup(row_width=2)
            buttons = [
                BButton(
                    text=await tr("Оплатить", u["locale"]),
                    callback_data=f"a:p:cfgs:extnd:{total_price}:{','.join(cfgs)}",
                ),
                BButton(text=await tr("Отмена", u["locale"]), callback_data="menu_cfg"),
            ]
            keyboard.add(*buttons)
            await bot.edit_message_text(
                text=text,
                chat_id=c.message.chat.id,
                message_id=c.message.id,
                reply_markup=keyboard,
            )

    elif c.data.startswith("a:p:cfgs:extnd"):
        total_price, cfgs_str = c.data.split(":")[4:]
        cfgs = set(cfgs_str.split(",")) if cfgs_str else set()
        if u["balance"] >= (total_price := int(total_price)) and len(cfgs) > 0:
            await db.execute(
                "UPDATE users SET balance = balance - %s WHERE id = %s and balance >= %s",
                (total_price, u["id"], total_price),
            )
            names = ""
            for cfg_id in cfgs:
                cfg = await db.fetchone(
                    "SELECT code_name, name FROM configs WHERE id=%s", (cfg_id,)
                )
                name = (
                    cfg["name"]
                    if cfg["name"]
                    else "".join(cfg["code_name"].split("_")[1:])
                )
                amount, unit = await to_msql(1)
                await db.execute(
                    "UPDATE configs SET valid_until=TIMESTAMPADD("
                    + unit
                    + ", %s, valid_until) WHERE id=%s",
                    (amount, cfg_id),
                )
            keyboard = BMarkup(
                keyboard=[
                    [
                        BButton(
                            text=await tr("BACK", u["locale"]), callback_data="menu_cfg"
                        )
                    ]
                ]
            )
            text = (await tr("CONFIGS_EXTEND_SUCCESS", u["locale"])).format(name=names)
            await bot.edit_message_text(
                text=text,
                chat_id=c.message.chat.id,
                message_id=c.message.id,
                reply_markup=keyboard,
            )
        elif len(cfgs) == 0:
            text = await tr("NO_CONFIGS_SELECTED", u["locale"])
            return await bot.answer_callback_query(
                callback_query_id=c.id, text=text, show_alert=True
            )
        else:
            text = await tr("INSUFFICIENT_FUNDS", u["locale"])
            kb = BMarkup(
                keyboard=[
                    [
                        BButton(
                            text=await tr("DEPOSIT", u["locale"]),
                            callback_data="baldeposit",
                        )
                    ],
                    [
                        BButton(
                            text=await tr("BACK", u["locale"]), callback_data="menu_cfg"
                        )
                    ],
                ]
            )
            return await bot.edit_message_text(
                text=text,
                chat_id=c.message.chat.id,
                message_id=c.message.id,
                reply_markup=kb,
            )

    # Input
    elif c.data.startswith("delete_mess"):
        try:
            return await bot.delete_message(c.message.chat.id, c.message.id)
        except Exception:
            pass


async def gen_key(tariff_k, u, loc_id):
    cfg_id = await db.execute(
        "INSERT INTO configs (user_id, location_id) VALUES (%s, %s)", (u["id"], loc_id)
    )
    location = await db.fetchone(
        "SELECT name, host, key_path, directory FROM locations WHERE id = %s", (loc_id,)
    )
    await db.execute(
        "UPDATE configs SET code_name=%s where id=%s",
        (cfg_name := f"{location['name']}_{u['username']}_{cfg_id}", cfg_id),
    )
    print("Generating key for", cfg_name)
    await ssh.new_key(
        location["host"], location["key_path"], location["directory"], cfg_name
    )
    print("Key generated")
    print("Getting key for", cfg_name)
    if location["host"] not in ("localhost", "127.0.0.1"):
        await ssh.get_key(
            location["host"], location["key_path"], location["directory"], cfg_name
        )
    print("Key gotten")
    await db.execute(
        "UPDATE users u JOIN configs c ON c.user_id = u.id SET u.configs_count = u.configs_count + 1, c.valid_until = %s, c.status='active' WHERE c.id = %s and u.id = %s",
        ((str(dt.now() + (await to_td(tariff_k))).split("."))[0], cfg_id, u["id"]),
    )
    return cfg_id


async def config_help(
    m: Message, text: str, cfg_codename: str, cfg_name: str | None = None
):
    # with open(os.path.join(CONF_DIR, str(cfg_codename) + ".conf"), "rb") as file:
    #    with open(os.path.join(CONF_DIR, str(cfg_codename)) + ".txt", "r") as f:
    #        txt = f.readline()
    #        await bot.send_document(
    #            chat_id=m.chat.id,
    #            document=types.InputFile(
    #                file, file_name="".join(cfg_codename.split("_")[1:]) + ".conf"
    #            ),
    #            caption=txt,
    #        )
    with open(os.path.join(CONF_DIR, str(cfg_codename) + ".png"), "rb") as qr:
        await bot.send_photo(chat_id=m.chat.id, photo=qr, caption=text)


async def to_td(tariff_k: int) -> td:
    if int(tariff_k) == 30:
        return td(minutes=30)
    return td(days=(30 * int(tariff_k)))


async def month_counter(tariff_k: int) -> str:
    t100 = tariff_k % 100
    if t100 >= 11 and t100 <= 14:
        return f"{tariff_k}месяцев"

    match tariff_k % 10:
        case 1:
            return f"{tariff_k}месяц"
        case 2:
            return f"{tariff_k}месяца"
        case 3:
            return f"{tariff_k}месяца"
        case 4:
            return f"{tariff_k}месяца"
        case _:
            return f"{tariff_k}месяцев"


async def to_msql(count: int) -> tuple[str, str]:
    if count == 30:
        return "30", "MINUTE"
    return str(count), "MONTH"


async def to_us(s: str, loc: str) -> str:
    s = s.strip().lower()
    if s.endswith("min"):
        return f"{s[:-3]} {await tr('MIN', loc)}"
    elif s.endswith("h"):
        return f"{s[:-1]} {await tr('H', loc)}"
    elif s.endswith("d"):
        return f"{s[:-1]} {await tr('D', loc)}"
    else:
        return f"1 {await tr('M', loc)}"


async def price_counter(count: int, price: int = base_price) -> int:
    return int(tariff_multip[count] * count * price / 100)


async def clear(u_id):
    if u_id in conf_changes.keys():
        del conf_changes[u_id]
    if u_id in balance_depos:
        del balance_depos[balance_depos.index(u_id)]
    if u_id in referals:
        del referals[referals.index(u_id)]


async def photo_handl(message: Message):
    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    photo = await bot.download_file(file_info.file_path)
    payment = await db.fetchone(
        "SELECT paid_at, id, user_id FROM payments WHERE message_id = %s",
        (message.reply_to_message.text.split()[1],),
    )
    file_name = f"{str(payment['paid_at'])}_{payment['id']}_{payment['user_id']}"


# daily check configs
async def daily_check(x):
    print("Daily check started")
    while True:
        await db.execute(
            "UPDATE configs SET status='expired' WHERE status='active' AND valid_until <= NOW()"
        )
        ban = await db.fetchall(
            "SELECT c.id, c.user_id, c.code_name,l.id as l_id , l.host, l.key_path, l.directory, u.tg_user_id, u.locale FROM configs c JOIN locations l ON c.location_id = l.id JOIN users u ON c.user_id=u.id WHERE c.status = 'expired' ORDER BY l.id"
        )
        for i in ban:
            await ssh.del_key(
                host=i["host"],
                ssh_key=i["key_path"],
                directory=i["directory"],
                cfg_name=i["code_name"],
            )
            await db.execute(
                "UPDATE users SET configs_count = GREATEST(configs_count - 1, 0) WHERE id=%s",
                (i["user_id"],),
            )
            text = (await tr("CONFIG_EXPIRED_DELETED", i["locale"])).format(
                code_name=i["code_name"]
            )
            try:
                await bot.send_message(i["tg_user_id"], text)
            except Exception:
                pass
            await db.execute(
                "UPDATE configs SET status='archived' WHERE id=%s", (i["id"],)
            )
        await asyncio.sleep(x)


async def day_chek():
    while True:
        print("Day check started")
        target = dt.now().replace(hour=12, minute=0, second=0, microsecond=0) + (
            td(days=1) if dt.now().hour >= 12 else td()
        )
        await asyncio.sleep((target - dt.now()).total_seconds())
        notifies = await db.fetchall(
            "SELECT DISTINCT u.id, u.tg_user_id, u.locale, u.first_name, u.username FROM configs c JOIN users u ON c.user_id = u.id WHERE c.status = 'active' AND c.valid_until >= NOW() and c.valid_until < NOW() + INTERVAL 2 DAY"
        )
        for notify in notifies:
            cfgs = await db.fetchall(
                "SELECT name, code_name, valid_until FROM configs WHERE status = 'active' AND valid_until >= NOW() and valid_until < NOW() + INTERVAL 2 DAY AND user_id = %s",
                (notify["id"],),
            )
            cfg_list = "\n".join(
                cfg["name"] + f" ({cfg['valid_until']})"
                if cfg["name"]
                else "".join(cfg["code_name"].split("_")[1:])
                + f" ({cfg['valid_until']})"
                for cfg in cfgs
            )
            text = (
                await tr(
                    "CONFIGS_EXPIRES" if cfg_list.count(",") == 0 else "CONFIG_EXPIRES",
                    notify["locale"],
                )
            ).format(name=cfg_list)
            try:
                await bot.send_message(notify["tg_user_id"], text)
            except Exception:
                await bot.send_message(
                    chat_id=ADMIN,
                    text=f"Не удалось отправить сообщение пользователю {notify['first_name']}({notify['usrname']})",
                )


async def main():
    try:
        r = await init_redis()
        await db.init_pool(db_host, db_port, db_user, db_pass, db_table)
        await bot.delete_webhook(drop_pending_updates=True)
        daily_task = asyncio.create_task(daily_check(900))
        day_task = asyncio.create_task(day_chek())
        bot_task = asyncio.create_task(
            bot.infinity_polling(
                allowed_updates=[
                    "message",
                    "callback_query",
                    "pre_checkout_query",
                    "successful_payment",
                ],
                request_timeout=120,
                skip_pending=True,
            )
        )
    finally:
        await close_redis()

    await asyncio.gather(daily_task, bot_task, day_task)


if __name__ == "__main__":
    asyncio.run(main())
