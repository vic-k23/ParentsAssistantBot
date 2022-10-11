from logging import debug, error

from aiogram import Dispatcher
from aiogram.dispatcher import filters

from .password_generator import get_password
from .start import start_command


def register_commands(dp: Dispatcher):
    try:
        dp.register_message_handler(start_command, commands=['start'])
        debug("Команда start зарегистрирована!")

        dp.register_message_handler(get_password, filters.Regexp(regexp=r"пароль(\d+)"))
        debug("Команда пароль зарегистрирована")
    except Exception as ex:
        error("Не удалось зарегистрировать команду start", *ex.args)
