from locale import currency
from telebot.async_telebot import AsyncTeleBot
import asyncio, os
from telebot import types
import subprocess
from dotenv import load_dotenv
import db
from datetime import datetime as dt
from datetime import timedelta as td
import json

#time.sleep(10)



# Load configuration
load_dotenv()
TOKEN = os.getenv('TOKEN')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN').strip()
CONF_DIR = os.getenv('CONF_DIR', './configs')
cfg_tariff = {"9min":7000, "59min":10000, "11h":12000, "23h":15000, "2d":20000, "7d":25000, "till end beta":66666}
pay_operations = dict()
conf_changes=dict()
balance_depos=[]


# Initialize bot
bot = AsyncTeleBot(TOKEN, parse_mode='HTML')


# Command Handlers
@bot.message_handler(commands=['start','s'])
async def send_welcome(m):
    u = await db.fetchone("SELECT id, locale FROM users WHERE tg_user_id=%s",
                          (m.from_user.id,))
    if not u:
        uid = await db.execute(
            "INSERT INTO users (tg_user_id, username, first_name, last_name) VALUES (%s, %s, %s, %s)",
            (m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
        )
        return await bot.send_message(m.chat.id, "Welcome! Use /help to see available commands.")
    elif u['locale'] == "en":
        await db.execute(
            "UPDATE users SET username=%s, first_name=%s, last_name=%s WHERE tg_user_id=%s",
            (m.from_user.username, m.from_user.first_name, m.from_user.last_name, m.from_user.id))
        await bot.send_message(m.chat.id, "Use /help to see available commands.")
    else:
        await db.execute(
            "UPDATE users SET username=%s, first_name=%s, last_name=%s WHERE tg_user_id=%s",
            (m.from_user.username, m.from_user.first_name, m.from_user.last_name, m.from_user.id))
        await bot.send_message(m.chat.id, "Напиши /help чтобы увидеть список доступных команд")
    await clear(m.from_user.id)



@bot.message_handler(commands=['menu', 'm'])
async def menu(m):
    u = await db.fetchone("SELECT id, balance, configs_count FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u:
        return await bot.reply_to(m, "Write first /start")
    else:
        menu_text = (
            f"Твой баланс {u['balance']}руб\n"
            f"У тебя {u['configs_count']} конфигов"
        )
        buttons = [
            types.InlineKeyboardButton(text="Мои конфиги", callback_data="menu_myconfigs"),
            types.InlineKeyboardButton(text="Новый конфиг", callback_data="menu_newconfig")
        ]
        keyboard = types.InlineKeyboardMarkup(row_width = 2)
        keyboard.add(*buttons)
        await bot.send_message(chat_id=m.chat.id, text=menu_text, reply_markup=keyboard)
        
    await clear(m.from_user.id)



@bot.message_handler(commands=['help','h'])
async def send_help(m):
    u = await db.fetchone("SELECT locale, admin_lvl FROM users WHERE tg_user_id=%s", (m.from_user.id))
    if not u or (u['locale'] == "en"):
        help_text = (
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/newconfig - Buy new config\n"
            "/myconfigs - Get all your configs\n"
            "/settings - Chenge name/descriptions of configs"
        )
    else:
        help_text = (
            "/start - Запустить бота\n"
            "/help - Отобразить это сообщение\n"
            "/newconfig - Купить новый конфиг\n"
            "/myconfigs - Получить все твои конфиги\n"
            "/settings - Изменить название/описание конфига\n"
            "/menu - Основное меню"
        )
    
    if (u['admin_lvl'] > 0) and (u['locale'] == "en"):
        help_text += ( "\n"
            ""
        )
    elif (u['admin_lvl'] > 0) and (u['locale'] == "ru"):
        help_text += (
            "\n/a - отобразить стоящие очереди"
        )
    await bot.reply_to(m, text=help_text)
    await clear(m.from_user.id)



@bot.message_handler(commands=['myconfigs', 'mycfg'])
async def myconfigs(m):
    u = await db.fetchone("SELECT id FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u:
        return await bot.send_message(m.chat.id, "Write first /start")
    
    rows = await db.fetchall("SELECT id, name, code_name FROM configs WHERE user_id=%s and status='active'",
                             (u['id']))
    
    if not rows:
        return await bot.send_message(m.chat.id, "У тебя пока нет конфигов.")
    else:
        buttons = [
            types.InlineKeyboardButton(text=(i["name"] if i["name"] else i["code_name"]), callback_data=f"show_config_{i['id']}")
            for i in rows
        ]
        keyboard=types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        await bot.send_message(m.chat.id, "Выбери конфиг", reply_markup=keyboard)
    await clear(m.from_user.id)



@bot.message_handler(commands = ['newconfig', 'newcfg', 'nwcfg'])
async def newconfig(m):
    u = await db.fetchone ("SELECT id, locale FROM users WHERE tg_user_id=%s", (m.from_user.id))
    if not u:
        return await bot.reply_to(m, "Write first /start")
    else:
        locations = await db.fetchall("SELECT id, name FROM locations WHERE is_active = 1")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton(text=i['name'], callback_data=f"config_loc_choose{i['id']}")
            for i in locations
        ]
        if u['locale'] == "ru":
            buttons.append(types.InlineKeyboardButton(text="Скоро...", callback_data="soon"))
            keyboard.add(*buttons)
            return await bot.send_message(m.chat.id, "Выбери локацию", reply_markup=keyboard)
        elif u ['locale'] == "en":
            buttons.append(types.InlineKeyboardButton(text="Soon...", callback_data="soon"))
            keyboard.add(*buttons)
            return await bot.send_message(m.chat.id, "Choose location", reply_markup=keyboard)
    await clear(m.from_user.id)


@bot.message_handler(commands = ['contin'])
async def contin(m):
    u = await db.fetchone("SELECT id FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u:
        return await bot.send_message(m.chat.id, "Write first /start")
    
    rows = await db.fetchall("SELECT id, name, code_name FROM configs WHERE user_id=%s and status='active'",
                             (u['id']))
    
    if not rows:
        return await bot.send_message(m.chat.id, "У тебя пока нет конфигов.")
    else:
        buttons = [
            types.InlineKeyboardButton(text=(i["name"] if i["name"] else i["code_name"]), callback_data=f"contin_config_{i['id']}")
            for i in rows
        ]
        keyboard=types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        await bot.send_message(m.chat.id, "Выбери конфиг", reply_markup=keyboard)
    await clear(m.from_user.id)


@bot.message_handler(commands = ['balance', 'bal'])
async def balance(m):
    u = await db.fetchone ("SELECT id, locale, balance FROM users WHERE tg_user_id=%s", (m.from_user.id))
    if not u:
        return await bot.reply_to(m, "Write first /start")
    else:
        buttons = [
            types.InlineKeyboardButton(text="Пополнить", callback_data="baldeposit")
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        await bot.send_message(m.chat.id, f"Твой баланс: {u['balance']}", reply_markup=keyboard)


@bot.message_handler(commands = ['settings', 'sett'])
async def description(m):
    u = await db.fetchone("SELECT id, locale, admin_lvl FROM users WHERE tg_user_id=%s", (m.from_user.id))
    if not u:
        return await bot.send_message(m, "Write frist /start")
    else:
        rows = await db.fetchall("SELECT id, name, code_name, location_id, valid_until FROM configs WHERE user_id=%s and status='active'", (u['id']))
        buttons = [
            types.InlineKeyboardButton(text=(x["name"] if x["name"] else x["code_name"]), callback_data=f"config_settings_{x['id']}")
            for x in rows
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        await bot.send_message(m.chat.id, "Выбери конфиг для изменения", reply_markup=keyboard)



@bot.message_handler(commands = ['a'])
async def operat(m):
    u = await db.fetchone("SELECT id, admin_lvl FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u or u['admin_lvl'] < 0:
        return await bot.send_message(m.chat.id, "This command not for you")
    else:
        await bot.send_message(m.chat.id, ("".join(pay_operations)+"\n" + str(conf_changes) if pay_operations or conf_changes else "No"))
        await bot.send_message(m.chat.id, str(dt.now()))



@bot.message_handler(chat_types=['private'], content_types=['text'])
async def message_hand(m):
    u = await db.fetchone("SELECT id, locale, admin_lvl FROM users WHERE tg_user_id=%s", (m.from_user.id))
    if not u:
        return await bot.send_message(m, "Write frist /start")
    elif m.from_user.id in conf_changes.keys():
        if conf_changes[m.from_user.id].split("_")[0] == "name":
            config_name = m.text
            if len(m.text) <= 32:
                cfg = await db.fetchone("SELECT name, code_name FROM configs WHERE user_id=(SELECT id FROM users WHERE tg_user_id=%s)", (m.from_user.id))
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                buttons = [
                    types.InlineKeyboardButton("Ok✅", callback_data=f"change_name_{conf_changes[m.from_user.id].split("_")[-1]}_{m.text}"),
                    types.InlineKeyboardButton("No❌", callback_data="delete_mess")
                ]
                keyboard.add(*buttons)
                del(conf_changes[m.from_user.id])
                await bot.send_message(m.chat.id, f"Ты хочешь заменить название конфига\n{cfg['name'] if cfg['name'] else cfg['code_name']}\nна\n{m.text}", reply_markup=keyboard)
            else:
                await bot.send_message(m.chat.id, "Слишком длинное название")
        elif conf_changes[m.from_user.id].split("_")[0] == "desc":
            config_desc = m.text
            if len(m.text) <= 255:
                cfg = await db.fetchone("SELECT description FROM configs WHERE user_id=(SELECT id FROM users WHERE tg_user_id=%s)", (m.from_user.id))
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                buttons = [
                    types.InlineKeyboardButton("Yes✅", callback_data=f"change_descript_{conf_changes[m.from_user.id].split("_")[-1]}_{m.text}"),
                    types.InlineKeyboardButton("No❌", callback_data="delete_mess")
                ]
                keyboard.add(*buttons)
                del(conf_changes[m.from_user.id])
                if cfg['description']:
                    await bot.send_message(m.chat.id, f"Ты хочешь заменить описание конфига\n{cfg['hint']}\nна\n{m.text}", reply_markup=keyboard)
                else:
                    await bot.send_message(m.chat.id, f"Ты хочешь поставить описание конфига\n{m.text}", reply_markup=keyboard)
            else:
                await bot.send_message(m.chat.id, "Слишком длинное описание")
                
    elif m.from_user.id in balance_depos:
        try:
            summ = int(m.text)
        except:
            return await bot.send_message(m.chat.id, "Отправь целое число")
        if summ < 80:
            return await bot.send_message(m.chat.id, "Сумма должна быть больше 80руб")
        price = [types.LabeledPrice(label=f"Balance deposit {summ}", amount=int(str(summ)+"00"))]
        payment_id = await db.execute('INSERT INTO payments (user_id, amount, currency, description) VALUES (%s, %s, %s, %s)',
                         (u['id'], summ, 'RUB', f"Deposit {m.from_user.id} balance, summ = {summ}"))
        pay_operations[f"balance_deposit_{summ}_{payment_id}"]=""
        await bot.send_invoice(chat_id=m.chat.id,
                               title=f"Пополнение {summ} для баланса {m.from_user.first_name}",
                               description=f"Пополнение внутриботового баланса {m.from_user.first_name}({m.from_user.id}) на {summ}руб",
                               invoice_payload=f"balance_deposit_{summ}_{payment_id}",
                               provider_token=PROVIDER_TOKEN,
                               currency="RUB",
                               prices=price,
                               photo_url="http://kirian.su/test/Money.png",
                               need_email=True,
                               send_email_to_provider=True)


@bot.pre_checkout_query_handler(func=lambda query: True)
async def pre_checkout(q):
    print("---------------------------------query---------------------------------")
    print(q)
    if q.invoice_payload in pay_operations.keys():
        if q.invoice_payload.startswith("newconfig"):
            await bot.answer_pre_checkout_query(q.id, ok=True)
            u = await db.fetchone ("SELECT id FROM users WHERE tg_user_id=%s", (q.from_user.id))
            await db.execute('INSERT INTO payments (user_id, config_id, amount, currency) VALUES (%s, %s, %s, %s)', (u['id'], q.invoice_payload.split("_")[-1], q.total_amount, q.currency))
        elif q.invoice_payload.startswith("config_contin"):
            await bot.answer_pre_checkout_query(q.id, ok=True)
            pay_operations[q.invoice_payload] = await db.execute('INSERT INTO payments (user_id, config_id, amount, currency, description) VALUES (%s, %s, %s, %s, %s)', (u['id'], q.invoice_payload.split("_")[-1], q.total_amount, q.currency, q.invoice_payload))
        elif q.invoice_payload.startswith("balance"):
            await bot.answer_pre_checkout_query(q.id, ok=True)
    else:
        await bot.answer_pre_checkout_query(q.id, ok=False, error_message="Error, try again or type message to bot's group")
    print("---------------------------------query---------------------------------")



@bot.message_handler(content_types=['successful_payment'])
async def successful_payment(m):
    print("---------------------------------successful_payment---------------------------------")
    payment = m.successful_payment
    if payment.invoice_payload.startswith("newconfig"):
        cfg_id = payment.invoice_payload.split("_")[-1]
        del(pay_operations[payment.invoice_payload])
        await db.execute("UPDATE payments SET status=%s, paid_at = CURRENT_TIMESTAMP(), raw_payload=%s, provider_tx_id=%s, telegram_tx_id=%s WHERE config_id=%s",
                        ('paid', json.dumps(m.json, ensure_ascii=False), payment.provider_payment_charge_id, payment.telegram_payment_charge_id, cfg_id))
        location = (await db.fetchone("SELECT name FROM locations AS l WHERE l.id = (SELECT location_id FROM configs WHERE id = %s)",(cfg_id)))['name']
        cfg_name = f"{location}_{m.from_user.username}_{cfg_id}"
        subprocess.run(['python3', 'awgcfg.py', '-a', cfg_name])
        subprocess.run(['python3', 'awgcfg.py', '-c', '--dir', str(CONF_DIR)])
        subprocess.run(['python3', 'awgcfg.py', '-q', '--dir', str(CONF_DIR)])
        subprocess.run(['systemctl', 'restart', 'awg-quick@awg0.service'])
        await db.execute('UPDATE `users` SET configs_count=configs_count + 1 WHERE tg_user_id=%s', (m.from_user.id))
        await db.execute("UPDATE configs SET valid_until=%s, status='active' WHERE id = %s",
                        ((str(dt.now()+(await to_td(payment.invoice_payload.split("_")[-2]))).split("."))[0], cfg_id))
        await bot.send_message(m.chat.id, text=("Спасибо за оплату!\n"
                                                "для использования конфига скачай любое из следующих предложений\n"
                                                "Android: <a href='https://play.google.com/store/apps/details?id=org.amnezia.vpn&pcampaignid=web_share'>AmneziaVPN</a> <a href='https://play.google.com/store/apps/details?id=org.amnezia.awg&pcampaignid=web_share'>AmneziaWG</a>\n"
                                                "Apple: <a href='https://apps.apple.com/us/app/amneziavpn/id1600529900'>AmneziaVPN</a> <a href='https://apps.apple.com/us/app/amneziawg/id6478942365'>AmneziaWG</a>\n"
                                                "Windows: <a href='https://github.com/amnezia-vpn/amnezia-client/releases/download/4.8.2.3/AmneziaVPN_4.8.2.3_x64.exe'>AmneziaVPN</a>"))
        with open(CONF_DIR+str(cfg_name)+".png", "rb") as qr:
            await bot.send_photo(m.chat.id, qr)
        with open(CONF_DIR+str(cfg_name)+".conf", "rb") as file:
            await bot.send_document(m.chat.id, document=types.InputFile(file, file_name="".join(cfg_name.split("_")[1:])+".conf"))
            
    elif payment.invoice_payload.startswith("balance"):
        summ = payment.invoice_payload.split("_")[-2]
        del(pay_operations[payment.invoice_payload])
        await db.execute("UPDATE payments SET status=%s, paid_at = CURRENT_TIMESTAMP(), raw_payload=%s, provider_tx_id=%s, telegram_tx_id=%s WHERE id=%s",
                        ('paid', json.dumps(m.json, ensure_ascii=False), payment.provider_payment_charge_id, payment.telegram_payment_charge_id, payment.invoice_payload.split("_")[-1]))
        await db.execute(f"UPDATE users SET balance = balance + {summ} WHERE tg_user_id={m.from_user.id}")
        await bot.send_message(m.chat.id, f"Баланс успешно пополнен на {summ}руб.")
        
    elif payment.invoice_payload.startswith("config_contin"):
        del(pay_operations[payment.invoice_payload])
        data = payment.invoice_payload.split("_")[-2:]
        amount, unit = await to_msql(data[0])
        cfg_id = int(data[1])
        await db.execute("UPDATE configs SET valid_until=TIMESTAMPADD("+unit+", %s, valid_until) WHERE id=%s", (amount, cfg_id))
        cfg = await db.fetchone("SELECT code_name, name FROM configs WHERE id=%s", (cfg_id))
        await bot.send_message(m.chat.id, text=(f"Конфиг {cfg["name"] if cfg["name"] else cfg["code_name"]} был успешно продлен"))
        
        
    print("---------------------------------successful_payment---------------------------------")



@bot.callback_query_handler(func = lambda c: any(c.data.startswith(i) for i in ["soon", "menu", "contin_config", "buy_contin_config", "config_loc_choose", "buy_config", "config_settings", "configs_name", "configs_descript", "delete_mess", "change_name", "change_descript", "show_config", "baldeposit"]))
async def  callback_query(c):
    u = await db.fetchone("SELECT id, admin_lvl, locale FROM users WHERE tg_user_id=%s", (c.from_user.id))
    if not u:
        return await bot.answer_callback_query(c.id, "Write first /start")
    if c.data.startswith("soon"):
        return await bot.answer_callback_query(c.id, "Function isn't work now, maybe soon...", show_alert=True)
    elif c.data.startswith("menu_config"):
        rows = await db.fetchall("SELECT id, name, code_name FROM configs WHERE user_id=%s and status='active'",
                                 (u['id']))
        if not(rows):
            return await bot.edit_message_text(text="У тебя нет конфигов в данный момент", chat_id=c.message.chat.id, message_id=c.message.id)
        buttons = [
            types.InlineKeyboardButton(text=(i["name"] if i["name"] else i["code_name"]), callback_data=f"show_config_{i['id']}")
            for i in rows
        ]
        keyboard=types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        await bot.edit_message_text(text="Выбери конфиг", chat_id=c.message.chat.id, message_id=c.message.id, reply_markup=keyboard)
    elif c.data.startswith("menu_newconfig"):
        locations = await db.fetchall("SELECT id, name FROM locations WHERE is_active = 1")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton(text=i['name'], callback_data=f"config_loc_choose{i['id']}")
            for i in locations
        ]
        if u['locale'] == "ru":
            buttons.append(types.InlineKeyboardButton(text="Скоро...", callback_data="soon"))
            keyboard.add(*buttons)
            return await bot.edit_message_text(text="Выбери локацию", chat_id=c.message.chat.id, message_id=c.message.id, reply_markup=keyboard)
        elif u ['locale'] == "en":
            buttons.append(types.InlineKeyboardButton(text="Soon...", callback_data="soon"))
            keyboard.add(*buttons)
            return await bot.edit_message_text(text="Choose location", chat_id=c.message.chat.id, message_id=c.message.id, reply_markup=keyboard)
    elif c.data.startswith("config_loc_choose"):
        buttons = [
            types.InlineKeyboardButton(text=x, callback_data=f"buy_config_{c.data.replace("config_loc_choose","")}_{x}") 
            for x in cfg_tariff.keys()
            ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        return await bot.edit_message_text(text="Выбери тариф конфига", chat_id=c.message.chat.id, message_id=c.message.id, reply_markup=keyboard)
    elif c.data.startswith("buy_config"):
        data = c.data.split("_")
        location = (await db.fetchone("SELECT name FROM locations WHERE id=%s",(int(data[-2]))))['name']
        cfg_id = await db.execute("INSERT INTO configs (user_id, location_id) VALUES (%s, %s)",(u['id'], int(data[-2])))
        await db.execute("UPDATE configs SET code_name=%s where id=%s",(f"{location}_{c.from_user.username}_{cfg_id}", cfg_id))
        await bot.delete_message(c.message.chat.id, c.message.id)
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
        return await bot.answer_callback_query(c.id, "")
    elif c.data.startswith("contin_config"):
        cfg_id = c.data.split("_")[-1]
        buttons = [
            types.InlineKeyboardButton(text=x, callback_data=f"buy_contin_config_{cfg_id}_{x}") 
            for x in cfg_tariff.keys()
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        return await bot.edit_message_text(text="Выбери тариф конфига", chat_id=c.message.chat.id, message_id=c.message.id, reply_markup=keyboard)
    elif c.data.startswith("buy_contin_config"):
        data = c.data.replace("buy_contin_config_", "").split("_")
        await bot.delete_message(c.message.chat.id, c.message.id)
        payload = f"config_contin_{str(str(dt.now()).split(":")[1])}_{data[-1]}_{data[-2]}"
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
        return await bot.answer_callback_query(c.id, "")
    elif c.data.startswith("show_config"):
        data = c.data.split("_")[-1]
        cfg = await db.fetchone("SELECT name, code_name,location_id, valid_until FROM configs where id = %s",(data))
        with open(CONF_DIR+cfg['code_name']+".png", "rb") as qr:
                await bot.send_photo(c.message.chat.id, qr)
        with open(os.path.join(CONF_DIR, cfg['code_name']+".conf"), 'rb') as file:
            location = (await db.fetchall("SELECT name FROM locations WHERE id = %s", (cfg['location_id'])))[0]
            await bot.send_document(c.message.chat.id, types.InputFile(file, file_name="".join(cfg['name'] if cfg['name'] else cfg['code_name'].split("_")[1:])+".conf"), caption=f"{location['name']}, действителен до: {cfg['valid_until']}(GMT+3)")
        await bot.answer_callback_query(c.id, "")
    elif c.data.startswith("config_settings"):
        conf_changes[c.from_user.id]=c.data.split("_")[-1]
        buttons = [
            types.InlineKeyboardButton(text="Название", callback_data=f"configs_name_{conf_changes[c.from_user.id]}"),
            types.InlineKeyboardButton(text="Описание", callback_data=f"configs_descript_{conf_changes[c.from_user.id]}")
            ]
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        return await bot.edit_message_text("Что ты хочешь изменить?", c.message.chat.id, c.message.id, reply_markup=keyboard)
    elif c.data.startswith("configs_name"):
        conf_changes[c.from_user.id]=f"name_{c.data.split('_')[-1]}"
        await bot.edit_message_text("Напиши название, которое хочешь поставить\nДля отмены введи любую команду", c.message.chat.id, c.message.id)
    elif c.data.startswith("configs_descript"):
        conf_changes[c.from_user.id]=f"desc_{c.data.split('_')[-1]}"
        await bot.edit_message_text("Напиши описание, которое хочешь поставить\nДля отмены введи любую команду", c.message.chat.id, c.message.id)
    elif c.data.startswith("delete_mess"):
        return await bot.delete_message(c.message.chat.id, c.message.id)
    elif c.data.startswith("change_name"):
        cfg_id = c.data.split("_")[1]
        text = "_".join(c.data.split("_")[2:])
        await db.execute("UPDATE configs SET name = %s WHERE id = %s", (text, cfg_id))
        await bot.edit_message_text("Название успешно изменено", c.message.chat.id, c.message.id)
    elif c.data.startswith("change_descript"):
        cfg_id = c.data.split("_")[1]
        text = "_".join(c.data.split("_")[2:])
        await db.execute("UPDATE configs SET description = %s WHERE id = %s", (text, cfg_id))
        await bot.edit_message_text("Название успешно изменено", c.message.chat.id, c.message.id)
    elif c.data.startswith("baldeposit"):
        balance_depos.append(c.from_user.id)
        await bot.edit_message_text("Напиши сумму пополнения(руб.):", c.message.chat.id, c.message.id)



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

async def to_msql(s: str) -> str:
    s = s.strip().lower()
    if s.endswith("min"):
        return f"{s[:-3]}", "MINUTE"
    elif s.endswith("h"):
        return f"{s[:-1]}", "HOUR"
    elif s.endswith("d"):
        return f"{s[:-1]}", "DAY"
    else:
        return f"1", "MONTH"
      


async def clear(u_id):
    if u_id in conf_changes.keys():
        del(conf_changes[u_id])
    if u_id in balance_depos:
        del(balance_depos[balance_depos.index(u_id)])



#daily check configs 
async def daily_check(x):
    d = dt.now()
    await asyncio.sleep(x - d.hour * 3600 - d.minute * 60 - d.second)
    while True:
        await db.execute("UPDATE configs SET status='expired' WHERE status='active' AND valid_until <= NOW()")
        ban = await db.fetchall(f"SELECT id, user_id, code_name FROM configs WHERE status ='expired' AND updated_at >= NOW() - INTERVAL {x} SECOND")
        for i in ban:
            u = await db.fetchone("SELECT tg_user_id, locale FROM users WHERE id=%s", (i['user_id']))
            subprocess.run(['python3', 'awgcfg.py', '-d', f"{i['code_name']}"])
            subprocess.run(['systemctl', 'restart', 'awg-quick@awg0.service'])
            await db.execute("UPDATE users SET configs_count = GREATEST(configs_count - 1, 0) WHERE id=%s", (i['user_id'],))
            await bot.send_message(u['tg_user_id'], f"Твой конфиг {i['code_name']} закончился и был удален")
            await db.execute(f"UPDATE configs SET status='archived' WHERE id={i['id']}")
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