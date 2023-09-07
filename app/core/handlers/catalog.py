from typing import Optional
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, InlineKeyboardButton, FSInputFile, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger
from pathlib import Path


catalog = [
    {
        'image': 'Oleg.png',
        'title': 'Олег Фомин',
        'job_title': 'Руководитель команды технической поддержки',
    }, {
        'image': 'Vlad.png',
        'title': 'Владислав Дорофеев',
        'job_title': 'Системный администратор',
    }, {
        'image': 'Radmir.png',
        'title': 'Радмир Марданшин',
        'job_title': 'Выездной системный администратор',
    }
]

catalog_messages: list[int] = []


class CatalogCallbackFactory(CallbackData, prefix='catalog'):
    action: str
    value: Optional[int] = None


async def show_catalog_handler(message: Message):
    logger.debug(f'show_catalog_handler({message=})')
    for (index, person) in enumerate(catalog):
        photo = FSInputFile(Path('data', 'catalog', person['image']))

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text='Повысить',
                callback_data=CatalogCallbackFactory(action='raise', value=index).pack()
            ),
            InlineKeyboardButton(
                text='Уволить',
                callback_data=CatalogCallbackFactory(action='fire', value=index).pack()
            ),
        )
        result = await message.answer_photo(
            photo,
            caption=f'<b>{person["title"]}</b>\n{person["job_title"]}',
            reply_markup=builder.as_markup()
        )
        catalog_messages.insert(0, result.message_id)
        logger.debug(f'{catalog_messages=}')


async def delete_catalog_messages(bot: Bot, chat_id: int):
    for message_id in catalog_messages:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    catalog_messages.clear()


async def raise_employee_callback(callback: CallbackQuery, callback_data: CatalogCallbackFactory, bot: Bot):
    logger.debug(f'raise_employee_callback({callback=}, {callback_data=})')
    await delete_catalog_messages(bot, callback.from_user.id)
    await callback.message.answer(f'Повысили сотрудника {catalog[callback_data.value]["title"]}')
    await callback.answer()


async def fire_employee_callback(callback: CallbackQuery, callback_data: CatalogCallbackFactory, bot: Bot):
    logger.debug(f'fire_employee_callback({callback=}, {callback_data=})')
    await delete_catalog_messages(bot, callback.from_user.id)
    await callback.message.answer(f'Уволили сотрудника {catalog[callback_data.value]["title"]}')
    await callback.answer()


def setup(dp: Dispatcher):
    """Подключает каталог к диспетчеру сообщений"""
    dp.message.register(show_catalog_handler, Command('show_catalog'))
    dp.callback_query.register(raise_employee_callback, CatalogCallbackFactory.filter(F.action == 'raise'))
    dp.callback_query.register(fire_employee_callback, CatalogCallbackFactory.filter(F.action == 'fire'))
