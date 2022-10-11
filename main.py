import logging

from aiogram import Bot, Dispatcher, executor

from commands.commands_manadger import register_commands
from config.settings import app_settings
from storage.storage_manager import initialize_db


logging.basicConfig(level=logging.DEBUG)

initialize_db()

tg_bot_settings = app_settings.tg_bot

bot = Bot(token=tg_bot_settings.api_token)
dp = Dispatcher(bot=bot)

register_commands(dp)

if __name__ == '__main__':
    executor.start_polling(dp)
