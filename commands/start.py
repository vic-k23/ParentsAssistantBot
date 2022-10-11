from aiogram.types import Message

from storage.storage_manager import get_user, register_user


async def start_command(msg: Message):
    """
    Обработчик команды /start
    """

    if await get_user(msg.from_user.id) is None:
        await register_user(msg.from_user.id, msg.from_user.username)
        await msg.answer("Приветствую вас! Я постараюсь быть вам хорошим подспорьем в воспитании!")
        await msg.answer("Для начала давайте добавим ваших детей. Это можно сделать командой /add_child.")
    else:
        await msg.answer(f"Здравствуйте, {msg.from_user.username}! Чем могу помочь?")
