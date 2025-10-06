from telebot.async_telebot import AsyncTeleBot
import asyncio, os
from telebot import types
import subprocess
from dotenv import load_dotenv
import db
from datetime import datetime as dt
from datetime import timedelta as td
import time

time.sleep(10)


# Load configuration
load_dotenv()
TOKEN = os.getenv('TOKEN')
ADMINS = list(map(int, os.getenv('ADMINS').split(',')))
ADMIN = os.getenv('ADMIN')
CONF_DIR = os.getenv('CONF_DIR', './configs')

# Initialize bot
bot = AsyncTeleBot(TOKEN, parse_mode='HTML')

# Command Handlers
@bot.message_handler(commands=['start','s'])
async def send_welcome(m):
    print(bot.get_updates())
    u = await db.fetchone("SELECT id, locale FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u:
        uid = await db.execute(
            "INSERT INTO users (tg_user_id, username, first_name, last_name) VALUES (%s, %s, %s, %s)",
            (m.from_user.id, m.from_user.username, m.from_user.first_name, m.from_user.last_name)
        )
        await bot.send_message(m.chat.id, "Welcome! Use /help to see available commands.")
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
        
    
@bot.message_handler(commands=['help','h'])
async def send_help(m):
    u = await db.fetchone("SELECT locale, admin_lvl FROM users WHERE tg_user_id=%s", (m.from_user.id))
    if not u or (u['locale'] == "en"):
        help_text = (
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/newconfig - Buy new config\n"
            "/myconfigs - Get all your configs\n"
            "/delconfig - Delete config"
        )
    else:
        help_text = (
            "/start - Запустить бота\n"
            "/help - Отобразить это сообщение\n"
            "/newconfig - Купить новый конфиг\n"
            "/myconfigs - Получить все твои конфиги\n"
            "/delconfig - Удалить конфиг"
        )
    
    if (u['admin_lvl'] > 0) and (u['locale'] == "en"):
        help_text += ( "\n"
            "/addloc - Add new location of configs"
        )
    elif (u['admin_lvl'] > 0) and (u['locale'] == "ru"):
        help_text += ( "\n"
            "/addloc - Добавить новую локацию конфигов"
        )
    await bot.reply_to(m, text=help_text)


@bot.message_handler(commands=['myconfigs', 'mycfg', 'mcfg'])
async def myconfigs(m):
    u = await db.fetchone("SELECT id FROM users WHERE tg_user_id=%s", (m.from_user.id,))
    if not u:
        return await bot.reply_to(m, "Сначала /start")
    
    rows = await db.fetchall("SELECT * FROM configs WHERE user_id=%s", (u['id']))
    
    if not rows:
        return await bot.reply_to(m, "У тебя пока нет конфигов.")
    else:
        for i in rows:
            with open(os.path.join(CONF_DIR, i['name']+".conf"), 'rb') as file:
                location = (await db.fetchall("SELECT name FROM locations WHERE id = %s", (i['location_id'])))[0]
                await bot.send_document(m.chat.id, file, caption=f"{location['name']}, действителен до: {i['valid_until']}(GMT+3)")
        return


@bot.message_handler(commands = ['newconfig', 'newcfg', 'ncfg'])
async def newconfig(m):
    u = await db.fetchone ("SELECT id, locale FROM users WHERE tg_user_id=%s", (m.from_user.id))
    if not u:
        return await bot.reply_to(m, "Write first /start")
    else:
        locations = await db.fetchall("SELECT id, name FROM locations WHERE is_active=1")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton(text=i['name'], callback_data=f"newcfg{i['id']}")
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
    '''
    elif u['id'] == 1:
        cfgs = (await db.fetchone("SELECT configs_count FROM users WHERE id=%s", (u['id'])))['configs_count']
        location = (await db.fetchone("SELECT "))
        subprocess.run(['python3', 'awgcfg.py', '-a', f"{}"]) #f"{cfgs+1}({u['id']})"])
        subprocess.run(['python3', 'awgcfg.py', '-c', '--dir', str(CONF_DIR)])
        await db.execute('UPDATE users SET configs_count=%s WHERE id=%s', (cfgs := (cfgs+1), u['id']))
        await db.execute('INSERT INTO configs (user_id, name, location_id, valid_until, price) VALUES (%s, %s, %s, %s, %s)',
                   (u['id'], f"{u['id']}({cfgs})", 1, "2025-10-05 15:00:00", 1337))
        with open(CONF_DIR+str(f"/{u['id']}({cfgs})")+".conf", "rb") as file:
            await bot.send_document(m.chat.id, file)
        return


@bot.message_handler(commands = ['delconfig'])
async def delconfig(m):
    u = await db.fetchone("SELECT id FROM users WHERE tg_user_id=%s", (m.from_user.id))
    if not u:
        return await bot.reply_to(m, "Write first /start")
    cfgs = await db.fetchall("SELECT * FROM configs WHERE user_id=%s", (u['id']))
    if not cfgs and u['locale'] == "en":
        return await bot.reply_to(m, "You don't have any configs")
    elif not cfgs and u['locale'] == "ru":
        return await bot.reply_to(m, "У тебя нет конфигов")
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton(text=f"{i['name']}", callback_data=f"delcfg{i['id']}")
            for i in cfgs
        ]
        keyboard.add(*buttons)
        if u['locale'] == "en":
            return await bot.send_message(m.chat.id, "Choose config:", reply_markup=keyboard)
        else:
            return await bot.send_message(m.chat.id, "Выбери конфиг:", reply_markup=keyboard)
            
            


@bot.message_handler(commands = ['addloc'])
async def addloc(m):
    u = await db.fetchone('SELECT id, status, admin_lvl, locale FROM users WHERE tg_user_id=%s', (m.from_user.id))
    if not u or u['admin_lvl'] < 1:
        if u['locale'] == 'ru':
            return await bot.send_message(m.chat.id, "У тебя нет прав на эту команду")
        elif u['locale'] == 'en':
            return await bot.send_message(m.chat.id, "You don't have enough rights to this command.")
        else:
            return await bot.send_message(m.chat.id, "Write first '/start'")
    elif u['admin_lvl'] > 0 or u['id'] == 1:
        if u['locale'] == 'ru':
            text = m
            await bot.send_message(m.chat.id, m.text)
            

@bot.message_handler(commands=['inline'])
async def send_inline_keyboard(m):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Button 1", callback_data="button1")
    button2 = types.InlineKeyboardButton(text="Button 2", callback_data="button2")
    keyboard.add(button1, button2)
    await bot.send_message(m.chat.id, "Choose an option:", reply_markup=keyboard)
        
    
    
        
    u = await db.fetchone("SELECT id FROM users WHERE tg_user_id=%s", (message.from_user.id,))
    if not u:
        await bot.send_message(message.chat.id, "You are not registered. Use /start to register.")
        return
    cfg_files = [f for f in os.listdir(CONF_DIR) if f.endswith('.conf')]
    if not cfg_files:
        await bot.reply_to(message, "No configuration files found.")
        return
    for cfg_file in cfg_files:
        with open(os.path.join(CONF_DIR, cfg_file), 'rb') as file:
            await bot.send_document(message.chat.id, file)
    await bot.reply_to(message, "All configuration files have been sent.")


 
@bot.message_handler(commands=['newcfg'])
async def newcfg(m):
    if int(m.from_user.id) not in ADMINS:
        await bot.reply_to(m, "You are not authorized to use this command.")
        return
    subprocess.run(['python3', 'awgcfg.py', '-a', ADMIN+"1"])
    subprocess.run(['python3', 'awgcfg.py', '-c', '--dir', str(CONF_DIR)])
    with open(CONF_DIR + '/'+ADMIN+"1"+".conf", 'rb') as awg_file:
        await bot.send_document(m.chat.id, awg_file)
        await bot.send_message(m.chat.id, os.getcwd())
    await bot.reply_to(m, "Configuration files have been generated.")


@bot.message_handler(commands=['sendcfg'])
async def sendcfg(m):
    if int(m.from_user.id) not in ADMINS:
        await bot.reply_to(m, "You are not authorized to use this command.")
        return
    cfg_files = [f for f in os.listdir(CONF_DIR) if f.endswith('.conf')]
    if not cfg_files:
        await bot.reply_to(m, "No configuration files found.")
        return
    for cfg_file in cfg_files:
        with open(os.path.join(CONF_DIR, cfg_file), 'rb') as file:
            await bot.send_document(m.chat.id, file)
    await bot.reply_to(m, "All configuration files have been sent.")


@bot.callback_query_handler(func=lambda c: c.data in ("button1", "button2"))
async def callback_query(c: types.CallbackQuery):
    await bot.answer_callback_query(c.id, f"You clicked {c.data}")
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Button 1", callback_data="button1")
    button2 = types.InlineKeyboardButton(text="Button 2", callback_data="button2")
    keyboard.add(button1, button2)
    await bot.edit_message_text(
        chat_id=c.message.chat.id,
        message_id=c.message.message_id,
        text=f"You clicked {c.data}",
        reply_markup=keyboard
    )
'''


@bot.callback_query_handler(func = lambda c: any(i in c.data for i in ["delcfg","newcfg","soon"]))
async def  callback_query(c):
    u = await db.fetchone("SELECT id, admin_lvl FROM users WHERE tg_user_id=%s", (c.from_user.id))
    if not u:
        return await bot.answer_callback_query(c.id, "Write first /start")
    if "newcfg" in c.data and u['admin_lvl'] > 0:
        cfgs = (await db.fetchone("SELECT configs_count FROM users WHERE id=%s", (u['id'])))['configs_count']
        location = (await db.fetchone("SELECT name FROM locations WHERE id=%s", (int(c.data.replace("newcfg", "")))))['name']
        cfg_id = await db.execute('INSERT INTO configs (user_id, name, location_id, valid_until) VALUES (%s, %s, %s, %s)',
                   (u['id'], None, int(c.data.replace("newcfg", "")), (str(dt.now()+td(seconds=20)).split("."))[0]))
        await db.execute("UPDATE configs SET name=%s WHERE id=%s", (f"{location}_{c.from_user.username}_{cfg_id}", cfg_id))
        subprocess.run(['python3', 'awgcfg.py', '-a', f"{location}_{c.from_user.username}_{cfg_id}"])
        subprocess.run(['python3', 'awgcfg.py', '-c', '--dir', str(CONF_DIR)])
        await db.execute('UPDATE users SET configs_count=%s WHERE id=%s', (cfgs := (cfgs+1), u['id']))
        with open(CONF_DIR+str(f"/{location}_{c.from_user.username}_{cfg_id}")+".conf", "rb") as file:
            await bot.send_document(c.message.chat.id, file)
        return await bot.answer_callback_query(c.id, "")
        
        
#daily check configs 
async def daily_check(x):
    d = dt.now()
    await asyncio.sleep(x - d.hour * 3600 - d.minute * 60 - d.second)
    while True:
        await db.execute("UPDATE configs SET status='expired' WHERE status='active' AND valid_until <= NOW()")
        print("hi")
        ban = await db.fetchall("SELECT id, user_id, name FROM configs WHERE status ='expired'")
        print("hi")
        for i in ban:
            u = await db.fetchone("SELECT tg_user_id, locale FROM users WHERE id=%s", (i['user_id']))
            subprocess.run(['python3', 'awgcfg.py', '-d', f"{i['name']}"])
            await db.execute("DELETE FROM configs WHERE id=%s", (i['id'],))
            await db.execute("UPDATE users SET configs=configs-1 WHERE id=%s", (i['user_id'],))
            await bot.send_message(u['tg_user_id'], f"Твой конфиг {i['name']} закончился и был удален")
        warn = await db.fetchall("SELECT c.id, c.user_id, c.name, TIMESTAMPDIFF(DAY, NOW(), c.valid_until) AS days_left FROM configs c WHERE c.status='active' AND c.valid_until > NOW() AND TIMESTAMPDIFF(DAY, NOW(), c.valid_until) BETWEEN 1 AND 3")
        for i in warn:
            u = await db.fetchone("SELECT tg_user_id, locale FROM users WHERE id=%s", (i['user_id']))
            if u:
                await bot.send_message(u['tg_user_id'], f"Твой конфиг {i['name']} истекает через {i['days_left']} дней")
        await asyncio.sleep(x)


async def main():
    await db.init_pool()
    await bot.delete_webhook(drop_pending_updates=True)
    daily_task = asyncio.create_task(daily_check(10))
    bot_task = asyncio.create_task(bot.infinity_polling(allowed_updates=['message','callback_query']))
    
    await daily_task
    await bot_task
    
if __name__ == '__main__':
    asyncio.run(main())