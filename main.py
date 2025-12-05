from locale import currency
from telebot.async_telebot import AsyncTeleBot
import asyncio, os, subprocess
from telebot import types
from telebot.types import InlineKeyboardButton as BButton
from telebot.types import InlineKeyboardMarkup as BMarkup
from dotenv import load_dotenv
from datetime import datetime as dt
from datetime import timedelta as td
import json
import secrets
import db
from dataclasses import dataclass
from translation import tr

# Load configuration
load_dotenv()

def required_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing required env var: {name}")
    return val.strip()

TOKEN = required_env('TOKEN')
PROVIDER_TOKEN = required_env('PROVIDER_TOKEN')
CONF_DIR = os.getenv('CONF_DIR', './configs')
REFERAL_ALPHABET = required_env('REFERAL_SYMBOLS')
cfg_tariff = {"9min":7000, "59min":10000, "11h":12000, "23h":15000, "2d":20000, "7d":25000, "1mo":66666}
pay_operations = dict()
conf_changes=dict()
balance_depos=[]
referals = []

# Initialize bot
bot = AsyncTeleBot(TOKEN, parse_mode='HTML')


# Command Handlers
@bot.message_handler(commands=['start','s'])
async def send_welcome(m):
    u = await db.fetchone("SELECT id, referal, locale FROM users WHERE tg_user_id=%s",
                          (m.from_user.id,))
    new_uid = None
    if not u:
        code = "".join(secrets.choice(REFERAL_ALPHABET) for _ in range(16))
        while (await db.fetchone("SELECT id FROM users WHERE referal_code=%s", (code,))):
            code = "".join(secrets.choice(REFERAL_ALPHABET) for _ in range(16))
        new_uid = await db.execute(
            "INSERT INTO users (tg_user_id, username, first_name, last_name, referal_code) VALUES (%s, %s, %s, %s, %s)",
            (m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name, code)
        )
        mess = m.text.split(maxsplit=1)
        ref = mess[1] if len(mess) > 1 else None
        text = await tr("START_MESS", 'en')
        await bot.send_message(text=text,
                               chat_id=m.chat.id)
        if ref:
            user = await db.fetchone("SELECT first_name, id FROM users WHERE referal_code=%s", (ref,))
            if user and user['id']:
                await db.execute("UPDATE users SET referal=%s WHERE id=%s", (ref, new_uid))
                text = (await tr("REFERAL_BECAME", 'en')).format(user=user['first_name'])
                await bot.send_message(text=text,
                                       chat_id=m.chat.id)
    else:
        await db.execute(
            "UPDATE users SET username=%s, first_name=%s, last_name=%s WHERE tg_user_id=%s",
            (m.from_user.username, m.from_user.first_name, m.from_user.last_name, m.from_user.id))

        text = await tr("START_MESS", u['locale'])
        await bot.send_message(text=text,
                               chat_id=m.chat.id)
    user_id = u['id'] if u else new_uid
    if user_id:
        await clear(user_id)



@bot.message_handler(commands=['menu', 'm'])
async def menu(m):
    u = await db.fetchone("SELECT id, locale, balance, configs_count FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u:
        text = await tr("NOT_USER", 'en')
        return await bot.send_message(text=text,
                                      chat_id=m.chat.id)
    else:
        keyboard = BMarkup()
        keyboard.row(BButton(text=await tr("My configs", u['locale']), callback_data="menu_config"))
        keyboard.row(BButton(text=await tr("Account", u['locale']), callback_data="account_menu"))
        keyboard.row(BButton(text=await tr("Information", u['locale']), callback_data="menu_information"))
        keyboard.row(BButton(text=await tr("Buy config", u['locale']), callback_data="choose_location_buy"))
        keyboard.row(BButton(text=await tr("Пополнить баланс", u['locale']), callback_data="baldeposit"))
        keyboard.row(BButton(text=await tr("LANG_CHANGE", u['locale']), callback_data="choose_language"))
        text = (await tr("MENU_MESS", u['locale'])).format(
            balance = u['balance'],
            count = u['configs_count']
        )
        await bot.send_message(text=text,
                               chat_id=m.chat.id,
                               reply_markup=keyboard)
    await clear(u['id'])



@bot.message_handler(commands=['help','h'])
async def send_help(m):
    u = await db.fetchone("SELECT id, locale, admin_lvl FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u:
        text = await tr("NOT_USER", 'en')
        return await bot.reply_to(text=text, message=m)
    text = await tr("HELP", u['locale'])
    if (u['admin_lvl'] > 0):
        text += await tr("ADMIN_HELP", u['locale'])
    await bot.send_message(text=text,
                           chat_id=m.chat.id)
    await clear(u['id'])



@bot.message_handler(commands = ['a'])
async def operat(m):
    u = await db.fetchone("SELECT id, admin_lvl FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u or u['admin_lvl'] < 0:
        text = await tr("ACESS_ERR", 'en')
        return await bot.send_message(text=text, chat_id=m.chat.id)
    else:
        await bot.send_message(m.chat.id, ("".join(pay_operations)+"\n" + str(conf_changes) if pay_operations or conf_changes else "No"))
        await bot.send_message(m.chat.id, str(dt.now()))



@bot.message_handler(commands = ['ref', 'referal'])
async def referal(m):
    u = await db.fetchone("SELECT id, locale, referal FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u:
        text = await tr("NOT_USER", 'en')
        return await bot.reply_to(text=text,
                                  message=m)
    else:
        try:
            code = m.text.split()[1]
            user = await db.fetchone("SELECT first_name, id FROM users WHERE referal_code=%s", (code,))
            if user and user['id'] and not u['referal']:
                await db.execute("UPDATE users SET referal=%s WHERE id=%s", (code, u['id']))
                text = (await tr("REFERAL_BECAME", u['locale'])).format(user=user['first_name'])
                await bot.send_message(text=text,
                                       chat_id=m.chat.id)
            else:
                text = await tr("REFERAL_ERR", u['locale'])
                await bot.send_message(text=text,
                                       chat_id=m.chat.id)
        except:
            referals.append(u['id'])
            text = await tr("INPUT_REFERAL", u['locale'])
            await bot.send_message(text=text,
                                   chat_id=m.chat.id)



@bot.message_handler(commands = ['sendall'])
async def sendall(m):
    u = await db.fetchone("SELECT id, admin_lvl, locale FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u or u['admin_lvl'] < 1:
        text = await tr("CMD_NOT_FOR_YOU", (u or {}).get('locale', 'en'))
        return await bot.send_message(m.chat.id, text)
    else:
        text = m.text.replace("/sendall ", "")
        rows = await db.fetchall("SELECT tg_user_id FROM users")
        for row in rows:
            try:
                await bot.send_message(chat_id=row['tg_user_id'], text=text)
                await asyncio.sleep(0.1)
            except:
                pass



@bot.message_handler(chat_types=['private'], content_types=['text'])
async def message_hand(m):
    u = await db.fetchone("SELECT id, locale, admin_lvl FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u:
        text = await tr("NOT_USER", 'en')
        return await bot.reply_to(text=text,
                                  message=m)
    elif u['id'] in conf_changes.keys():
        if conf_changes[u['id']].split("_")[0] == "name":
            config_name = m.text
            if len(m.text) <= 32:
                cfg_id = conf_changes[u['id']].split("_")[1]
                cfg = await db.fetchone("SELECT name, code_name FROM configs WHERE id=%s", (cfg_id,))
                keyboard = BMarkup(row_width=1)
                buttons = [
                    BButton(text=await tr("YES", u['locale']), callback_data=f"change_name_{cfg_id}"),
                    BButton(text=await tr("CANCEL", u['locale']), callback_data="delete_mess")
                ]
                keyboard.add(*buttons)
                conf_changes[u['id']] = config_name
                name = cfg['name'] if cfg['name'] else "".join(cfg['code_name'].split("_")[1:])
                text = (await tr("CHANGING_CONFIG_NAME", u['locale'])).format(old_name=name, new_name=m.text)
                await bot.send_message(text=text,
                                       chat_id=m.chat.id,
                                       reply_markup=keyboard)
            else:
                text = await tr("TOO_LONG_NAME", u['locale'])
                await bot.send_message(text=text, chat_id=m.chat.id)
        elif conf_changes[u['id']].split("_")[0] == "desc":
            config_desc = m.text
            if len(m.text) <= 255:
                cfg_id = conf_changes[u['id']].split("_")[1]
                cfg = await db.fetchone("SELECT description FROM configs WHERE id=%s", (cfg_id,))
                keyboard = BMarkup(row_width=2)
                buttons = [
                    BButton(text=await tr("YES", u['locale']), callback_data=f"change_descript_{cfg_id}_{m.text}"),
                    BButton(text=await tr("CANCEL", u['locale']), callback_data="delete_mess")
                ]
                keyboard.add(*buttons)
                del(conf_changes[u['id']])
                if cfg['description']:
                    text = (await tr("CHANGING_CONFIG_DESC", u['locale'])).format(old_desc=cfg['description'], new_desc=config_desc)
                    await bot.send_message(text=text,
                                           chat_id=m.chat.id,
                                           reply_markup=keyboard)
                else:
                    text = (await tr("SET_CONFIG_DESC", u['locale'])).format(new_desc=config_desc)
                    await bot.send_message(m.chat.id, text, reply_markup=keyboard)
            else:
                text = await tr("TOO_LONG_DESC", u['locale'])
                await bot.send_message(m.chat.id, text)
    elif u['id'] in balance_depos:
        try:
            summ = int(m.text)
        except:
            text = await tr("SEND_INT", u['locale'])
            return await bot.send_message(text=text,
                                          chat_id=m.chat.id)
        if summ <= 80:
            text = (await tr("MIN_AMOUNT", u['locale'])).format(min=80)
            return await bot.send_message(text=text,
                                          chat_id=m.chat.id)
        price = [types.LabeledPrice(label=f"Balance deposit {summ}", amount=int(str(summ)+"00"))]
        payment_id = await db.execute(
            'INSERT INTO payments (user_id, amount, currency, description) VALUES (%s, %s, %s, %s)',
            (u['id'], summ, 'RUB', f"Deposit {m.from_user.id} balance, summ = {summ}")
        )
        pay_operations[f"balance_deposit_{summ}_{payment_id}"] = ""
        if u['locale'] == "en":
            title=f"Deposit {summ} for {m.from_user.first_name}"
            description=f"Deposit in-bot balance {m.from_user.first_name}({m.from_user.id}) for {summ}rub"
        else:
            title=f"Пополнение {summ} для баланса {m.from_user.first_name}"
            description=f"Пополнение внутриботового баланса {m.from_user.first_name}({m.from_user.id}) на {summ}руб"
        await bot.send_invoice(chat_id=m.chat.id,
                               title=title,
                               description=description,
                               invoice_payload=f"balance_deposit_{summ}_{payment_id}",
                               provider_token=PROVIDER_TOKEN,
                               currency="RUB",
                               prices=price,
                               photo_url="http://kirian.su/test/Money.png",
                               need_email=True,
                               send_email_to_provider=True)
    elif u['id'] in referals:
        code = m.text.strip().split()[0]
        user = await db.fetchone('SELECT id, first_name FROM users WHERE referal_code=%s', (code,))
        if user and user['id']:
            await db.execute("UPDATE users SET referal=%s WHERE id=%s", (code, u['id']))
            text = (await tr("REFERAL_BECAME", u['locale'])).format(user=user['first_name'])
        else:
            text = await tr("REFERAL_ERR", u['locale'])
        await bot.send_message(text=text,
                               chat_id=m.chat.id)



@bot.pre_checkout_query_handler(func=lambda query: True)
async def pre_checkout(q):
    u = await db.fetchone("SELECT id FROM users WHERE tg_user_id=%s", (q.from_user.id,))
    if q.invoice_payload in pay_operations.keys():
        if q.invoice_payload.startswith("newconfig"):
            await bot.answer_pre_checkout_query(q.id, ok=True)
            await db.execute(
                'INSERT INTO payments (user_id, config_id, amount, currency) VALUES (%s, %s, %s, %s)',
                (u['id'], q.invoice_payload.split("_")[-1], q.total_amount, q.currency)
            )
        elif q.invoice_payload.startswith("config_contin"):
            await bot.answer_pre_checkout_query(q.id, ok=True)
            pay_operations[q.invoice_payload] = await db.execute(
                'INSERT INTO payments (user_id, config_id, amount, currency, description) VALUES (%s, %s, %s, %s, %s)',
                (u['id'], q.invoice_payload.split("_")[-1], q.total_amount, q.currency, q.invoice_payload)
            )
        elif q.invoice_payload.startswith("balance"):
            await bot.answer_pre_checkout_query(q.id, ok=True)
    else:
        err = await tr("PRECHECKOUT_ERROR", 'en')
        await bot.answer_pre_checkout_query(q.id, ok=False, error_message=err)



@bot.message_handler(content_types=['successful_payment'])
async def successful_payment(m):
    u = await db.fetchone("SELECT id, locale FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    payment = m.successful_payment
    if payment.invoice_payload.startswith("newconfig"):
        cfg_id = payment.invoice_payload.split("_")[-1]
        del(pay_operations[payment.invoice_payload])
        await db.execute(
            "UPDATE payments SET status=%s, paid_at = CURRENT_TIMESTAMP(), raw_payload=%s, provider_tx_id=%s, telegram_tx_id=%s WHERE config_id=%s",
            ('paid', json.dumps(m.json, ensure_ascii=False), payment.provider_payment_charge_id, payment.telegram_payment_charge_id, cfg_id)
        )
        location = (await db.fetchone("SELECT name FROM locations AS l WHERE l.id = (SELECT location_id FROM configs WHERE id = %s)", (cfg_id,)))['name']
        cfg_name = f"{location}_{m.from_user.username}_{cfg_id}"
        subprocess.run(['python3', 'awgcfg.py', '-a', cfg_name])
        subprocess.run(['python3', 'awgcfg.py', '-c', '--dir', str(CONF_DIR)])
        subprocess.run(['python3', 'awgcfg.py', '-q', '--dir', str(CONF_DIR)])
        subprocess.run(['systemctl', 'restart', 'awg-quick@awg0.service'])
        await db.execute('UPDATE `users` SET configs_count=configs_count + 1 WHERE tg_user_id=%s', (m.from_user.id,))
        await db.execute(
            "UPDATE configs SET valid_until=%s, status='active' WHERE id = %s",
            ((str(dt.now()+(await to_td(payment.invoice_payload.split("_")[-2]))).split("."))[0], cfg_id)
        )
        text = await tr("CONFIG_HELP", u['locale'])
        await bot.send_message(text=text,
                               chat_id=m.chat.id)
        with open(os.path.join(CONF_DIR,str(cfg_name)+".png"), "rb") as qr:
            await bot.send_photo(m.chat.id, qr)
        with open(os.path.join(CONF_DIR,str(cfg_name)+".conf"), "rb") as file:
            await bot.send_document(m.chat.id, document=types.InputFile(file, file_name="".join(cfg_name.split("_")[1:])+".conf"))
    elif payment.invoice_payload.startswith("balance"):
        summ = payment.invoice_payload.split("_")[-2]
        del(pay_operations[payment.invoice_payload])
        await db.execute(
            "UPDATE payments SET status=%s, paid_at = CURRENT_TIMESTAMP(), raw_payload=%s, provider_tx_id=%s, telegram_tx_id=%s WHERE id=%s",
            ('paid', json.dumps(m.json, ensure_ascii=False), payment.provider_payment_charge_id, payment.telegram_payment_charge_id, payment.invoice_payload.split("_")[-1])
        )
        await db.execute("UPDATE users SET balance = balance + %s WHERE tg_user_id=%s", (int(summ), m.from_user.id))
        text = (await tr("BALANCE_DEPOSIT_SUCCESS", u['locale'])).format(amount=summ)
        await bot.send_message(text=text,
                               chat_id=m.chat.id)
    elif payment.invoice_payload.startswith("config_contin"):
        del(pay_operations[payment.invoice_payload])
        data = payment.invoice_payload.split("_")[-2:]
        amount, unit = await to_msql(data[0])
        cfg_id = int(data[1])
        await db.execute(
            "UPDATE configs SET valid_until=TIMESTAMPADD("+unit+", %s, valid_until) WHERE id=%s",
            (amount, cfg_id)
        )
        cfg = await db.fetchone("SELECT code_name, name FROM configs WHERE id=%s", (cfg_id,))
        name = cfg["name"] if cfg["name"] else "".join(cfg["code_name"].split("_")[1:])
        text = (await tr("CONFIG_EXTEND_SUCCESS", u['locale'])).format(name=name)
        await bot.send_message(text=text,
                               chat_id=m.chat.id)



@bot.callback_query_handler(func = lambda c: any(c.data.startswith(i) for i in ["soon", "menu", "config", "extend", "buy", "pay", "accept", "delete_mess", "change", "show", "baldeposit", "account", "referal", "choose", "set"]))
async def  callback_query(c):
    u = await db.fetchone("SELECT id, admin_lvl, locale, balance, configs_count FROM users WHERE tg_user_id=%s", (c.from_user.id,))
    if not u:
        text = await tr("NOT_USER", 'en')
        return await bot.answer_callback_query(callback_query_id=c.id,
                                               text=text)
    if c.data.startswith("soon"):
        text = await tr("SOON_FUNC", u['locale'])
        return await bot.answer_callback_query(text=text,
                                               callback_query_id=c.id,
                                               show_alert=True)

    #Input
    elif c.data.startswith("menu_config"):
        rows = await db.fetchall("SELECT id, name, code_name FROM configs WHERE user_id=%s and status='active'",
                                 (u['id'],))
        if not(rows):
            text = await tr("NO_CONFIGS", u['locale'])
            return await bot.edit_message_text(text=text,
                                               chat_id=c.message.chat.id,
                                               message_id=c.message.id)
        buttons = [
            BButton(text=(i["name"] if i["name"] else "".join(i["code_name"].split("_")[1:])), callback_data=f"config_menu_{i['id']}")
            for i in rows
        ]
        keyboard=BMarkup(row_width=1)
        keyboard.add(*buttons)
        text = await tr("CHOOSE_CONFIG", u['locale'])
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output config_menu_(config id)

    #Input
    elif c.data.startswith("menu_main"):
        keyboard = BMarkup()
        keyboard.row(BButton(text=await tr("My configs", u['locale']), callback_data="menu_config"))
        keyboard.row(BButton(text=await tr("Account", u['locale']), callback_data="account_menu"))
        keyboard.row(BButton(text=await tr("Information", u['locale']), callback_data="menu_information"))
        keyboard.row(BButton(text=await tr("Buy config", u['locale']), callback_data="choose_location_buy"))
        keyboard.row(BButton(text=await tr("Пополнить баланс", u['locale']), callback_data="baldeposit"))
        keyboard.row(BButton(text=await tr("LANG_CHANGE", u['locale']), callback_data="choose_language"))
        text = (await tr("MENU_MESS", u['locale'])).format(
            balance = u['balance'],
            count = u['configs_count']
        )
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output menu_config / account_menu / menu_information / choose_location
    
    #Input
    elif c.data.startswith("choose_language"):
        buttons = [
            BButton(text="🇷🇺Русский(RU)", callback_data="set_language_ru"),
            BButton(text="🇬🇧English(UK)", callback_data="set_language_en")
        ]
        keyboard = BMarkup(row_width=1)
        keyboard.add(*buttons)
        text = "Choose language / Выберите язык"
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output set_language_(ru/en)
    
    #Input _(ru/en)
    elif c.data.startswith("set_language"):
        lang = c.data.split("_")[-1]
        await db.execute("UPDATE users SET locale=%s WHERE id=%s", (lang, u['id']))
        text = await tr("LANG_SET_SUCCESS", lang)
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id)
    #Output Message

    #Input _(config id)
    elif c.data.startswith("config_menu"):
        cfg_id = c.data.split("_")[-1]
        cfg = await db.fetchone("SELECT name, code_name, valid_until, description FROM configs WHERE id=%s", (cfg_id,))
        name = "".join((cfg['name'] if cfg['name'] else cfg['code_name'].split("_")[1:]))
        description = cfg['description'] or "-"
        buttons = [
            BButton(text=await tr("BTN_SHOW_QR", u['locale']), callback_data=f"show_config_qr_{cfg_id}"),
            BButton(text=await tr("BTN_GET_FILE", u['locale']), callback_data=f"show_config_conf_{cfg_id}"),
            BButton(text=await tr("BTN_EXTEND_CONFIG", u['locale']), callback_data=f"extend_config_{cfg_id}"),
            BButton(text=await tr("BTN_EDIT_CONFIG", u['locale']), callback_data=f"config_settings_{cfg_id}")
        ]
        keyboard=BMarkup(row_width=1)
        keyboard.add(*buttons)
        text = (await tr("CONFIG_MENU", u['locale'])).format(
            name=name,
            valid_until=cfg['valid_until'],
            description=description
        )
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output show_config_qr_(config id) / show_config_conf_(config id) / extend_config_(config id) / config_settings_(config id)

    #Input choose_location_(type)
    elif c.data.startswith("choose_location"):
        type = c.data.split("_")[-1]
        locations = await db.fetchall("SELECT id, name FROM locations WHERE is_active = 1")
        keyboard = BMarkup(row_width=2)
        buttons = [
            BButton(text=i['name'], callback_data=f"choose_tariff_{type}_{i['id']}")
            for i in locations
        ]
        buttons.append(BButton(text=await tr("BTN_SOON", u['locale']), callback_data="soon"))
        keyboard.add(*buttons)
        text = await tr("CHOOSE_LOCATION", u['locale'])
        return await bot.edit_message_text(text=text, chat_id=c.message.chat.id, message_id=c.message.id, reply_markup=keyboard)
    #Output choose_tariff_(type)_(location id)

    #Input _(type)_(location id/config id)
    elif c.data.startswith("choose_tariff"):
        type, loc_id = c.data.split("_")[2:]
        buttons = [
            BButton(text=x, callback_data=f"choose_pay_{type}_{loc_id}_{x}") 
            for x in cfg_tariff.keys()
        ]
        keyboard = BMarkup(row_width=2)
        keyboard.add(*buttons)
        text = await tr("Vpn duration", u['locale'])
        return await bot.edit_message_text(text=text,
                                           chat_id=c.message.chat.id,
                                           message_id=c.message.id,
                                           reply_markup=keyboard)
    #Output _(location id)_(tariff key)

    #Input _(type)_(location id)_(tariff key)
    elif c.data.startswith("choose_pay"):
        type, loc_id, tariff_k = c.data.split("_")[2:]
        if type == "buy":
            buttons = [
                BButton(text="ЮKassa", callback_data=f"buy_config_{loc_id}_{tariff_k}"),
                BButton(text=await tr("Пополнить баланс", u['locale']), callback_data=f"pay_config_{loc_id}_{tariff_k}")
            ]
        elif type == "extend":
            buttons = [
                BButton(text="ЮKassa", callback_data=f"buy_extend_config_{loc_id}_{tariff_k}"),
                BButton(text=await tr("Пополнить баланс", u['locale']), callback_data=f"pay_extend_config_{loc_id}_{tariff_k}")
            ]
        keyboard = BMarkup(row_width = 2)
        keyboard.add(*buttons)
        amount_rub = cfg_tariff[tariff_k] / 100
        text = (await tr("PAY_SUMMARY", u['locale'])).format(
            amount=int(amount_rub),
            balance=u['balance']
        )
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output 

    #Input _(location id)_(tariff key)
    elif c.data.startswith("buy_config"):
        await bot.delete_message(c.message.chat.id, c.message.id)
        data = c.data.split("_")
        location = (await db.fetchone("SELECT name FROM locations WHERE id=%s",(int(data[-2]),)))['name']
        cfg_id = await db.execute("INSERT INTO configs (user_id, location_id) VALUES (%s, %s)",(u['id'], int(data[-2])))
        await db.execute("UPDATE configs SET code_name=%s where id=%s",(f"{location}_{c.from_user.username}_{cfg_id}", cfg_id))
        payload=f"newconfig_payload_{data[-1]}_{cfg_id}"
        pay_operations[payload] = ""
        prices = [types.LabeledPrice(label=f"Config for {data[-1]}", amount=cfg_tariff[data[-1]])]
        await bot.send_invoice(chat_id=c.message.chat.id,
                                      title=f"test {data[-1]} config pay",
                                      description=f"test description for {data[-1]} config pay, card for pay: 2200 0000 0000 0004 11/11 111",
                                      invoice_payload=payload,
                                      provider_token=PROVIDER_TOKEN,
                                      currency='RUB',
                                      prices=prices,
                                      photo_url="http://kirian.su/test/VPW.jpg",
                                      need_email=True,
                                      send_email_to_provider=True)
    #Output Message(invoice), pay_operations["newconfig_payload_(triff key)_(config id)"] = ""

    #Input _(location id)_(tariff key)
    elif c.data.startswith("pay_config"):
        loc_id, tariff_k = c.data.split("_")[2:]
        summ = int(str(cfg_tariff[tariff_k])[:-2])
        summ = int(summ/100*95)
        if u['balance'] >= summ:
            text = (await tr("PAY_FROM_BALANCE", u['locale'])).format(
                amount=summ,
                balance=u['balance']
            )
            keyboard = BMarkup(row_width=2)
            buttons = [
                BButton(text = await tr("Оплатить", u['locale']), callback_data=f"accept_pay_config_{loc_id}_{summ}_{tariff_k}"),
                BButton(text = await tr("Отмена", u['locale']), callback_data=f"delete_mess")
            ]
            keyboard.add(*buttons)
            await bot.edit_message_text(text = text,
                                        chat_id=c.message.chat.id,
                                        message_id=c.message.id,
                                        reply_markup=keyboard)
    #Output accept_pay_config_(location id)_(summ) / delete_mess

    #Input _(location id)_(summ)_(tariff key)
    elif c.data.startswith("accept_pay_config"):
        loc_id, summ, tariff_k = c.data.split("_")[3:]
        if u['balance'] >= (summ := int(summ)):
            await db.execute("UPDATE users SET balance = %s WHERE id = %s",
                             (u['balance'] - summ, u['id']))
            location = (await db.fetchone("SELECT name FROM locations WHERE id=%s",(int(loc_id),)))['name']
            cfg_id = await db.execute("INSERT INTO configs (user_id, location_id) VALUES (%s, %s)",
                                      (u['id'], int(loc_id)))
            cfg_name = f"{location}_{c.from_user.username}_{cfg_id}"
            subprocess.run(['python3', 'awgcfg.py', '-a', cfg_name])
            subprocess.run(['python3', 'awgcfg.py', '-c', '--dir', str(CONF_DIR)])
            subprocess.run(['python3', 'awgcfg.py', '-q', '--dir', str(CONF_DIR)])
            subprocess.run(['systemctl', 'restart', 'awg-quick@awg0.service'])
            await db.execute("UPDATE configs SET code_name=%s where id=%s",(cfg_name, cfg_id))
            await db.execute('UPDATE `users` SET configs_count=configs_count + 1 WHERE id=%s', (u['id'],))
            await db.execute("UPDATE configs SET valid_until=%s, status='active' WHERE id = %s",
                             ((str(dt.now()+(await to_td(tariff_k))).split("."))[0], cfg_id))
            text = await tr("CONFIG_HELP", u['locale'])
            await bot.send_message(text = text,
                                   chat_id = c.message.chat.id)
            with open(os.path.join(CONF_DIR,str(cfg_name)+".png"), "rb") as qr:
                await bot.send_photo(chat_id=c.message.chat.id,
                                     photo = qr)
            with open(os.path.join(CONF_DIR,str(cfg_name)+".conf"), "rb") as file:
                await bot.send_document(chat_id = c.message.chat.id,
                                        document=types.InputFile(file, file_name="".join(cfg_name.split("_")[1:])+".conf"))
    #Output Message(config_help, qr code, document)

    #Input _(config id)
    elif c.data.startswith("extend_config"):
        cfg_id = c.data.split("_")[-1]
        buttons = [
            BButton(text=x, callback_data=f"buy_extend_config_{cfg_id}_{x}") 
            for x in cfg_tariff.keys()
        ]
        keyboard = BMarkup(row_width=2)
        keyboard.add(*buttons)
        text = await tr("CHOOSE_CONFIG_TARIFF", u['locale'])
        return await bot.edit_message_text(text=text, chat_id=c.message.chat.id, message_id=c.message.id, reply_markup=keyboard)
    #Output buy_extend_config_(config id)_(tariff key)

    #Input buy_extend_config_(config id)_(tariff key)
    elif c.data.startswith("buy_extend_config"):
        cfg_id, tariff_k = c.data.split("_")[3:]
        data = c.data.replace("buy_contin_config_", "").split("_")
        await bot.delete_message(c.message.chat.id, c.message.id)
        payload = f"config_contin_{str(str(dt.now()).split(':')[1])}_{data[-1]}_{data[-2]}"
        pay_operations[payload] = ""
        prices = [types.LabeledPrice(label=f"continue config {data[-2]}", amount=cfg_tariff[data[-1]])]
        await bot.send_invoice(chat_id=c.message.chat.id,
                                      title=f"test {data[-2]} config continue",
                                      description=f"test description for {data[-2]} config continue, card for pay: 2200 0000 0000 0004 11/11 111",
                                      invoice_payload=payload,
                                      provider_token=PROVIDER_TOKEN,
                                      currency='RUB',
                                      prices=prices,
                                      photo_url="http://kirian.su/test/VPW.jpg",
                                      need_email=True,
                                      send_email_to_provider=True)
    #Output Message(invoice), pay_operations[config_contin_(time)_(tariff key)_(config id)] := ""

    #Input pay_extend_config_(config id)_(tariff key)
    elif c.data.startswith("pay_extend_config"):
        cfg_id, tariff_k = c.data.split("_")[3:]
        summ = int(str(cfg_tariff[tariff_k])[:-2])
        summ = int(summ/100*95)
        if u['balance'] >= summ:
            text = (await tr("PAY_FROM_BALANCE", u['locale'])).format(
                amount=summ,
                balance=u['balance']
            )
            keyboard = BMarkup(row_width=2)
            buttons = [
                BButton(text = await tr("Оплатить", u['locale']), callback_data=f"accept_pay_extend_{cfg_id}_{summ}_{tariff_k}"),
                BButton(text = await tr("Отмена", u['locale']), callback_data=f"delete_mess")
            ]
            keyboard.add(*buttons)
            await bot.edit_message_text(text = text,
                                        chat_id=c.message.chat.id,
                                        message_id=c.message.id,
                                        reply_markup=keyboard)
    #Output accept_pay_extend_(config id)_(summ)_(tariff key) / delete_mess

    #Input _(config id)_(summ)_(tariff key)
    elif c.data.startswith("accept_pay_extend"):
        await bot.delete_message(c.message.chat.id, c.message.id)
        cfg_id, summ, tariff_k = c.data.split("_")[3:]
        if u['balance'] >= (summ := int(summ)):
            amount, unit = await to_msql(tariff_k)
            await db.execute("UPDATE users SET balance = %s WHERE id = %s",
                             (u['balance'] - summ, u['id']))
            await db.execute("UPDATE configs SET valid_until=TIMESTAMPADD("+unit+", %s, valid_until) WHERE id=%s", (amount, cfg_id))
            cfg = await db.fetchone("SELECT code_name, name FROM configs WHERE id=%s", (cfg_id,))
            name = cfg["name"] if cfg["name"] else "".join(cfg["code_name"].split("_")[1:])
            text = (await tr("CONFIG_EXTEND_SUCCESS", u['locale'])).format(name=name)
            await bot.send_message(text=text,
                                   chat_id=c.message.chat.id)

    #Input _(config id)
    elif c.data.startswith("show_config_conf"):
        await bot.delete_message(c.message.chat.id, c.message.id)
        cfg_id = c.data.split("_")[-1]
        cfg = await db.fetchone("SELECT name, code_name,location_id, valid_until FROM configs WHERE id = %s",
                                (cfg_id,))
        name = "".join(cfg['name'] if cfg['name'] else cfg['code_name'].split("_")[1:])
        with open(os.path.join(CONF_DIR, cfg['code_name']+".conf"), 'rb') as file:
            location = (await db.fetchall("SELECT name FROM locations WHERE id = %s", (cfg['location_id'],)))[0]
            caption = (await tr("CONFIG_VALID_UNTIL", u['locale'])).format(date=cfg['valid_until'])
            await bot.send_document(chat_id=c.message.chat.id,
                                    document=types.InputFile(file, file_name=name+".conf"),
                                    caption=caption)
    #Output Message(document)

    #Input _(config id)
    elif c.data.startswith("show_config_qr"):
        await bot.delete_message(c.message.chat.id, c.message.id)
        cfg_id = c.data.split("_")[-1]
        cfg = await db.fetchone("SELECT name, code_name FROM configs WHERE id = %s", (cfg_id,))
        name = "".join((cfg['name'] if cfg['name'] else cfg['code_name']).split("_")[1:])
        with open(os.path.join(CONF_DIR, cfg['code_name']+".png"), "rb") as qr:
                await bot.send_photo(chat_id=c.message.chat.id, photo=qr, caption=name)
    #Output Message(photo)

    #Input _(config id)
    elif c.data.startswith("config_settings"):
        cfg_id=c.data.split("_")[-1]
        conf_changes[u['id']]=cfg_id
        buttons = [
            BButton(text="Название", callback_data=f"config_name_{cfg_id}"),
            BButton(text="Описание", callback_data=f"config_descript_{cfg_id}")
        ]
        keyboard = BMarkup(row_width=1)
        keyboard.add(*buttons)
        text = await tr("CONFIG_SETTINGS_PROMPT", u['locale'])
        return await bot.edit_message_text(text, c.message.chat.id, c.message.id, reply_markup=keyboard)
    #Output config_name_(config id) / config_descript_(config id) ; conf_changes[u[id]] = (config id)

    #Input _(config id)
    elif c.data.startswith("config_name"):
        cfg_id=c.data.split('_')[-1]
        conf_changes[u['id']]=f"name_{cfg_id}"
        cfg = await db.fetchone("SELECT name, code_name FROM configs WHERE id=%s", (cfg_id,))
        name = "".join((cfg['name'] if cfg['name'] else cfg['code_name'].split("_")[1:]))
        text = (await tr("ASK_CONFIG_NAME", u['locale'])).format(name=name)
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id)
    #Output Message, conf_changes[u[id]] := name_(config_id)

    #Input _(config id)
    elif c.data.startswith("config_descript"):
        cfg_id=c.data.split('_')[-1]
        conf_changes[u['id']]=f"desc_{cfg_id}"
        cfg = await db.fetchone("SELECT name, code_name FROM configs WHERE id=%s", (cfg_id,))
        name = "".join((cfg['name'] if cfg['name'] else cfg['code_name'].split("_")[1:]))
        text = (await tr("ASK_CONFIG_DESC", u['locale'])).format(name=name)
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id)
    #Output Message, conf_changes[u[id]] := desc_(config_id) 

    #Input _(config id)
    elif c.data.startswith("change_name"):
        cfg_id = c.data.split("_")[2]
        text_val = conf_changes[u['id']]
        cfg = await db.fetchone("SELECT code_name FROM configs WHERE id=%s", (cfg_id,))
        await db.execute("UPDATE configs SET name = %s WHERE id = %s", (text_val, cfg_id))
        msg = (await tr("CONFIG_NAME_CHANGED", u['locale'])).format(
            code_name=cfg['code_name'],
            text=text_val
        )
        await bot.edit_message_text(text=msg,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id)
    #Output Message, change name in db

    #Input _(config id)
    elif c.data.startswith("change_descript"):
        cfg_id = c.data.split("_")[2]
        text_val = "_".join(c.data.split("_")[3:])
        await db.fetchone("SELECT code_name, name FROM configs WHERE id=%s",(cfg_id,))
        await db.execute("UPDATE configs SET description = %s WHERE id = %s", (text_val, cfg_id))
        msg = (await tr("CONFIG_DESC_CHANGED", u['locale'])).format(text=text_val)
        await bot.edit_message_text(text=msg,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id)
    #Output Message, change description in db

    #Input
    elif c.data.startswith("baldeposit"):
        balance_depos.append(u['id'])
        keyboard = BMarkup()
        keyboard.row(BButton(text=await tr("CANCEL", u['locale']), callback_data="cancel_deposit"))
        text = await tr("ASK_DEPOSIT_SUM", u['locale'])
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output Message, balance_depos.append(u[id]) / cancel_deposit

    #Input
    elif c.data.startswith("cancel_deposit"):
        balance_depos.remove(u['id'])
        keyboard = BMarkup()
        keyboard.row(BButton(text=await tr("BACK", u['locale']), callback_data="menu_main"))
        text = await tr("DEPOSIT_CANCELED", u['locale'])
        await bot.edit_message_text(text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output remove u[id] from balance_depos

    #Input
    elif c.data.startswith("account_menu"):
        keyboard = BMarkup()
        keyboard.row(BButton(text=await tr("REFERRAL_PROGRAM", u['locale']), callback_data="referal_menu"))
        keyboard.row(BButton(text=await tr("BACK", u['locale']), callback_data="menu_main"))
        text = await tr("ACCOUNT_MENU_TITLE", u['locale'])
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output referal_menu / menu_main

    #Input
    elif c.data.startswith("referal_menu"):
        keyboard=BMarkup()
        keyboard.row(BButton(text=await tr("BTN_MY_REF_CODE", u['locale']), callback_data="referal_get"))
        keyboard.row(BButton(text=await tr("BTN_INPUT_REF_CODE", u['locale']), callback_data="referal_became"))
        keyboard.row(BButton(text=await tr("BACK", u['locale']), callback_data="account_menu"))
        text = await tr("REFERRAL_MENU_TITLE", u['locale'])
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output referal_get / referal_became / account_menu

    #Input
    elif c.data.startswith("referal_became"):
        referals.append(u['id'])
        text = await tr("REFERRAL_ENTER_CODE", u['locale'])
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id)
    #Output referals.append(u[id])

    #Input
    elif c.data.startswith("referal_get"):
        code = (await db.fetchone("SELECT referal_code FROM users WHERE id = %s", (u['id'],)))['referal_code']
        keyboard=BMarkup()
        keyboard.row(BButton(text=await tr("BTN_COPY_CODE", u['locale']), copy_text=types.CopyTextButton(text=code)))
        keyboard.row(BButton(
            text=await tr("BTN_COPY_LINK", u['locale']),
            copy_text=types.CopyTextButton(text=f"https://t.me/{(await bot.get_me()).username}?start={code}")
        ))
        keyboard.row(BButton(text=await tr("BACK", u['locale']), callback_data="referal_menu"))
        text = (await tr("REF_CODE_TEXT", u['locale'])).format(code=code)
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output Copy_text / referal_menu

    #Input
    elif c.data.startswith("menu_information"):
        keyboard=BMarkup()
        keyboard.row(BButton(text=await tr("BOT_CHANNEL", u['locale']), url="https://t.me/Kirians_dev"))
        keyboard.row(BButton(text=await tr("BACK", u['locale']), callback_data="menu_main"))
        text = await tr("BOT_INFO", u['locale'])
        await bot.edit_message_text(text=text,
                                    chat_id=c.message.chat.id,
                                    message_id=c.message.id,
                                    reply_markup=keyboard)
    #Output Url / menu_main

    #Input
    elif c.data.startswith("delete_mess"):
        return await bot.delete_message(c.message.chat.id, c.message.id)


async def to_td(s: str) -> td:
    s = s.strip().lower()
    if s.endswith("min"):
        return td(minutes=int(s[:-3]))
    elif s.endswith("h"):
        return td(hours=int(s[:-1]))
    elif s.endswith("d"):
        return td(days=int(s[:-1]))
    else:
        return td(days=30)

async def to_msql(s: str) -> tuple[str, str]:
    s = s.strip().lower()
    if s.endswith("min"):
        return s[:-3], "MINUTE"
    elif s.endswith("h"):
        return s[:-1], "HOUR"
    elif s.endswith("d"):
        return s[:-1], "DAY"
    else:
        return "1", "MONTH"
      

async def clear(u_id):
    if u_id in conf_changes.keys():
        del(conf_changes[u_id])
    if u_id in balance_depos:
        del(balance_depos[balance_depos.index(u_id)])
    if u_id in referals:
        del(referals[referals.index(u_id)])



#daily check configs 
async def daily_check(x):
    while True:
        await db.execute("UPDATE configs SET status='expired' WHERE status='active' AND valid_until <= NOW()")
        ban = await db.fetchall(f"SELECT id, user_id, code_name FROM configs WHERE status ='expired' AND updated_at >= NOW() - INTERVAL {x} SECOND")
        for i in ban:
            u = await db.fetchone("SELECT tg_user_id, locale FROM users WHERE id=%s", (i['user_id'],))
            subprocess.run(['python3', 'awgcfg.py', '-d', f"{i['code_name']}"])
            subprocess.run(['systemctl', 'restart', 'awg-quick@awg0.service'])
            await db.execute("UPDATE users SET configs_count = GREATEST(configs_count - 1, 0) WHERE id=%s", (i['user_id'],))
            text = (await tr("CONFIG_EXPIRED_DELETED", u['locale'])).format(code_name=i['code_name'])
            await bot.send_message(u['tg_user_id'], text)
            await db.execute("UPDATE configs SET status='archived' WHERE id=%s", (i['id'],))
        '''
        warn = await db.fetchall("SELECT c.id, c.user_id, c.name, DATEDIFF(c.valid_until, CURDATE()) AS days_left FROM configs c WHERE c.status='active' AND c.valid_until x`x`x`x` NOW() AND DATEDIFF(c.valid_until, CURDATE())=1")
        for i in warn:
            u = await db.fetchone("SELECT tg_user_id, locale FROM users WHERE id=%s", (i['user_id']))
            if u:
                await bot.send_message(u['tg_user_id'], f"Твой конфиг {i['name']} истекает через {i['days_left']} дней")
        '''
        await asyncio.sleep(x)



async def main():
    await db.init_pool()
    await bot.delete_webhook(drop_pending_updates=True)
    daily_task = asyncio.create_task(daily_check(600))
    bot_task = asyncio.create_task(bot.infinity_polling(
        allowed_updates=['message', 'callback_query', 'pre_checkout_query', 'successful_payment'],
        request_timeout=60,
        skip_pending=True ))
    
    await asyncio.gather(daily_task, bot_task)



if __name__ == '__main__':
    asyncio.run(main())
