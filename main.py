from telebot.async_telebot import AsyncTeleBot
import asyncio
from telebot import types
import configparser
import os
import watchdog
import psutil

    
config = configparser.ConfigParser()
config.read('cfg.cfg')
TOKEN = config['Bot']['Token']
bot = AsyncTeleBot(TOKEN, parse_mode='HTML')
admins = set(map(str, config['Bot']['admins_id'].split(',')))
admin = config['Bot']['admin']
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message, "Welcome! Use /help to see available commands.")
    
@bot.message_handler(commands=['help'])
async def send_help(message):
    help_text = (
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/echo <text> - Echo the text back to you\n"
        "/inline - Show inline keyboard"
    )
    await bot.reply_to(message, help_text)

@bot.message_handler(commands=['echo'])
async def echo_message(message):
    text_to_echo = message.text.partition(' ')[2]
    if text_to_echo:
        await bot.reply_to(message, text_to_echo)
    else:
        await bot.reply_to(message, "Please provide text to echo.")

@bot.message_handler(commands=['inline'])
async def send_inline_keyboard(message):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Button 1", callback_data="button1")
    button2 = types.InlineKeyboardButton(text="Button 2", callback_data="button2")
    keyboard.add(button1, button2)
    await bot.send_message(message.chat.id, "Choose an option:", reply_markup=keyboard)

@bot.message_handler(commands=['newcfg'])
async def newcfg(message):
    if str(message.from_user.id) not in admins:
        await bot.reply_to(message, "You are not authorized to use this command.")
        return
    await bot.reply_to(message, "Configuration files have been generated.")

@bot.message_handler(commands = ['newA'])
async def newA(message):
    global aboba
    aboba = message.text
    await bot.reply_to(message, f"Set to {aboba}")

    
@bot.callback_query_handler(func=lambda c: c.data in ("button1", "button2"))
async def callback_query(c: types.CallbackQuery):
    print(c)
    await bot.answer_callback_query(c.id, f"You clicked {c.data}")
    await bot.edit_message_text(
        chat_id=c.message.chat.id,
        message_id=c.message.message_id,
        text=f"You clicked {c.data}"
    )

async def main():
    await bot.infinity_polling(allowed_updates=['message','callback_query'], restart_on_change=True)
    
if __name__ == '__main__':
    asyncio.run(main())