from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from voice.text_to_speach import speechify_text_to_speach
from config import voice_languages, article_link


start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🗣 Озвучить', callback_data='voice'),
        InlineKeyboardButton(text='📘 Инструкция', url=article_link)],
    [InlineKeyboardButton(text='💰 Пополнить баланс', callback_data='deposit')]
])

voice_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎤 Выбрать голос', callback_data='choose_voice')],
    [InlineKeyboardButton(text='✍️ Написать текст', callback_data='input_text')],
    [InlineKeyboardButton(text='⬅️ Вернуться назад', callback_data='back')]
])

start_voice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🗣 Озвучить', callback_data='input_text')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_menu')]
])

choose_voice_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎤 Выбрать голос', callback_data='choose_voice'),
        InlineKeyboardButton(text='❌ Отмена', callback_data='back')]
])

gender_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👨 Мужской', callback_data='gender_man'),
        InlineKeyboardButton(text='👩 Женский', callback_data='gender_woman')],
    [InlineKeyboardButton(text='🔙 Отмена', callback_data='back_to_menu')]
])

back_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❌ Отмена', callback_data='back')]
])

dep_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💰 Пополнить баланс', callback_data='deposit')],
    [InlineKeyboardButton(text='❌ Отмена', callback_data='back')]
])


async def voices(gender: str):
    voices = await speechify_text_to_speach.get_voices(gender)
    
    kb_builder = InlineKeyboardBuilder()
    for v in voices:
        kb_builder.add(InlineKeyboardButton(text=f'{v.title()} {voice_languages[v]}', callback_data=f'set_voice_{v}'))
    
    kb_builder.adjust(2)
    
    return kb_builder.as_markup()
