from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, \
    KeyboardButtonRequestChat, KeyboardButtonRequestUser, KeyboardButtonPollType, InlineKeyboardButton, CallbackQuery
from loguru import logger
from pathlib import Path
from uuid import uuid4


async def start_handler(message: Message):
    logger.debug(f'start_handler({message=})')

    text = (f'👋 Добрый день, {message.from_user.full_name}.\n\n'
            f'⚠️ Это тестовый бот, никакой полезной работы он не делает.\n\n'
            f'⚙️ Основные команды:\n'
            f'<b>/show_special_buttons</b>\n'
            f'<b>/show_inline_buttons</b>\n'
            f'<b>/show_button_with_data</b>\n'
            f'<b>/show_password_generator</b>\n'
            f'<b>/show_catalog</b>\n'
            f'\n🛠 Твой Telegram ID — {message.from_user.id}\n'
            f'\n❤️ Разработчик — @eldarofficialbot')

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Представиться', request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(text=text, reply_markup=keyboard)


async def contact_handler(message: Message):
    logger.debug(f'contact_handler({message=})')
    text = f'🪪 <b>Получена карточка контакта</b>\n\n'

    if message.contact.user_id:
        text += f'ID: {message.contact.user_id}\n'

    text += f'Имя: {message.contact.first_name}\n'
    if message.contact.last_name:
        text += f'Фамилия: {message.contact.last_name}\n'

    text += f'Номер телефона: {message.contact.phone_number}'

    if message.contact.vcard:
        text += f'vСard: {message.contact.vcard}\n'

    if message.contact.user_id == message.from_user.id:
        text += '\n\n✅ Это твой контакт'

    await message.reply(text)


async def authorize_handler(message: Message):
    logger.debug(f'authorize_handler({message=})')
    if message.contact.user_id == message.from_user.id:
        text = (f'Твой номер телефона: {message.contact.phone_number}\n\n'
                f'Запомнить этот номер?')
        await message.reply(text)
    else:
        await message.reply('❌ Это не твой контакт')


async def image_handler(message: Message, bot: Bot):
    logger.debug(f'image_handler({message=})')
    await message.reply(f'Классное фото, на какой фотик снято?')
    file = await bot.get_file(message.photo[-1].file_id)
    await bot.download_file(file.file_path, Path('data', 'temp', f'{uuid4().hex}.jpg'))


async def special_buttons_handler(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text='Запрос геолокации', request_location=True),
        KeyboardButton(text='Запрос контакта', request_contact=True)
    )
    builder.row(KeyboardButton(
        text='Создать викторину',
        request_poll=KeyboardButtonPollType(type='quiz'))
    )
    builder.row(
        KeyboardButton(
            text='Выбрать пользователя',
            request_user=KeyboardButtonRequestUser(
                request_id=1,
                user_is_premium=True
            )
        ),
        KeyboardButton(
            text='Выбрать группу',
            request_chat=KeyboardButtonRequestChat(
                request_id=2,
                chat_is_channel=True,
                chat_is_forum=True
            )
        )
    )

    await message.answer(
        'Выберите действие:',
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


async def inline_buttons_handler(message: Message, bot: Bot):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text='Ссылка на GitHub', url='https://github.com')
    )
    builder.row(InlineKeyboardButton(
        text='Ссылка на канал Telegram',
        url='tg://resolve?domain=telegram')
    )

    user_id = message.from_user.id
    chat_info = await bot.get_chat(user_id)
    if not chat_info.has_private_forwards:
        builder.row(InlineKeyboardButton(
            text='Ссылка на пользователя',
            url=f'tg://user?id={user_id}')
        )

    await message.answer(
        'Выберите ссылку:',
        reply_markup=builder.as_markup(),
    )


async def button_with_data_handler(message: Message):
    logger.debug(f'button_with_data_handler({message=})')
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='Отправить',
        callback_data=f'data_value'
    ))
    await message.answer(
        'Отправить команду?',
        reply_markup=builder.as_markup()
    )


async def button_with_data_callback(callback: CallbackQuery, bot: Bot):
    logger.debug(f'data_value_handler({callback=}, {bot=})')
    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id
    )
    await callback.answer(
        text='Команда отправлена',
        show_alert=True
    )


async def other_message_handler(message: Message):
    logger.debug(f'other_message_handler({message=})')
    text = (f'<b>Получено сообщение</b>\n\n'
            f'Тип: {message.content_type}')
    if message.text:
        text += f'\nТекст: {message.text}'
    await message.reply(text)


def setup(dp: Dispatcher):
    """Подключает базовые функции к диспетчеру сообщений"""
    dp.message.register(start_handler, CommandStart())
    dp.message.register(contact_handler, F.content_type == 'contact')
    # dp.message.register(authorize_handler, (F.content_type == 'contact') & (F.text == 'Представиться'))
    dp.message.register(image_handler, F.Photo)
    dp.message.register(special_buttons_handler, Command('show_special_buttons'))
    dp.message.register(inline_buttons_handler, Command('show_inline_buttons'))
    dp.message.register(button_with_data_handler, Command('show_button_with_data'))
    dp.callback_query.register(button_with_data_callback, F.data == 'data_value')
    dp.message.register(other_message_handler)
