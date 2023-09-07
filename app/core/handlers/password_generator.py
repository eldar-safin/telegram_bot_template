import random
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from loguru import logger


def password_generator_text():
    chars_list = list(map(chr, range(65, 91))) + list(map(chr, range(97, 123))) + [str(i) for i in range(0, 9)]
    return ''.join(random.choices(chars_list, k=12))


def password_generator_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='Повторить',
            callback_data='password_generator__repeat'
        ),
        InlineKeyboardButton(
            text='Завершить',
            callback_data='password_generator__finish'
        )
    )
    return builder.as_markup()


async def password_generator_handler(message: Message):
    await message.answer(
        text=password_generator_text(),
        reply_markup=password_generator_keyboard()
    )


async def password_generator_callback(callback: CallbackQuery):
    logger.debug(f'password_generator_callback({callback=})')
    message = callback.message
    answer_message = None
    if callback.data.split('__')[1] == 'repeat':
        await message.edit_text(password_generator_text(), reply_markup=password_generator_keyboard())
        answer_message = 'Сгенерирован новый пароль'
    else:
        await message.edit_reply_markup()
    await callback.answer(answer_message)


def setup(dp: Dispatcher):
    """Подключает генератор к диспетчеру сообщений"""
    dp.message.register(password_generator_handler, Command('show_password_generator'))
    dp.callback_query.register(password_generator_callback, F.data.startswith('password_generator'))
