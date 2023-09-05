from aiogram.types import Message
from loguru import logger


async def start_handler(message: Message):
    logger.debug(f'start_handler({message=})')
    await message.reply(f'Привет, {message.from_user.full_name}')
