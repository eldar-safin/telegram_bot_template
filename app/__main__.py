import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from .core.settings import settings
from .core.handlers import basic as basic_handlers
from .core.handlers import password_generator as password_generator_handlers
from .core.handlers import catalog as catalog_handlers


async def on_bot_startup(bot: Bot):
    logger.debug(f'on_bot_startup({bot=})')
    if settings.bot.admin_id:
        await bot.send_message(settings.bot.admin_id, text='Бот запущен')


async def on_bot_shutdown(bot: Bot):
    logger.debug(f'on_bot_shutdown({bot=})')
    if settings.bot.admin_id:
        await bot.send_message(settings.bot.admin_id, text='Бот остановлен')


async def start():
    logger.debug('start()')
    bot = Bot(token=settings.bot.token.get_secret_value(), parse_mode=ParseMode.HTML)
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.startup.register(on_bot_startup)
    dispatcher.shutdown.register(on_bot_shutdown)

    password_generator_handlers.setup(dispatcher)
    catalog_handlers.setup(dispatcher)
    basic_handlers.setup(dispatcher)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
