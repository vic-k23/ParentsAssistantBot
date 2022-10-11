from re import Match

from aiogram.types import Message

from services.pass_gen import generate_password


async def get_password(msg: Message, regexp: Match):
    if int(regexp.group(1)) < 8:
        await msg.reply(await generate_password(10))
    else:
        await msg.reply(await generate_password(int(regexp.group(1))))
