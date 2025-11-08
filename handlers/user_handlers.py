from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, ContentType
from aiogram.fsm.context import FSMContext
import asyncio

from keyboards import user_kbs
from states.user_states import UserState
from database.services.user_service import UserService
from middleware.db_di import DatabaseDI
from voice.speechify_text_to_speach import speechify_text_to_speach
from init_bot import bot

import os


router = Router()
router.message.middleware(DatabaseDI())
router.callback_query.middleware(DatabaseDI())


@router.message(CommandStart())
async def start(message: Message, user_service: UserService):
    user = await user_service.get(message.from_user.id)

    new = False
    if not user:
        user = await user_service.create_if_not_exists(message.from_user.id)
        await user_service.update_balance(user.tg_id, 5)
        new = True

    photo = FSInputFile("images/start.jpg")
    await message.answer_photo(
        photo,
        caption=f"<b>👋 Привет, здесь ты можешь озвучить свой текст разными голосами людей\n\nВаш баланс: {user.balance}⭐️\nХватит на: {user.balance * 150} символов\n\n<blockquote>Качественная озвучка\nБыстрая обработка\nНизкие цены (1 ⭐️ - 150 символов)\nОкругление символов по законам математики\nДо 2000 символов за 1 запрос</blockquote>\n\nИспользуй кнопки ниже👇</b>",
        reply_markup=user_kbs.start_kb,
    )

    if new:
        await message.answer(
            "<b>Спасибо за то что выбрали нас! На ваш счет пополнено 5⭐️</b>"
        )


@router.callback_query(F.data == "voice")
async def voice_handler(callback: CallbackQuery, user_service: UserService):
    await callback.answer()

    user = await user_service.get(callback.from_user.id)

    voice = (
        user.voice.title()
        if user.voice
        else "не выбран\n\nНеобходимо указать голос для озвучки"
    )

    await callback.message.answer(
        f"<b>⚡️ Выберите опцию для продолжения\n\nВыбранный голос: {voice}</b>",
        reply_markup=user_kbs.voice_kb,
    )


@router.callback_query(F.data.startswith("choose_voice"))
async def choose_voice(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.edit_text(
            "<b>🧍 Выберите пол для голоса</b>", reply_markup=user_kbs.gender_kb
        )
    except:
        await callback.message.answer(
            "<b>🧍 Выберите пол для голоса</b>", reply_markup=user_kbs.gender_kb
        )


@router.callback_query(F.data.startswith("gender"))
async def choose_voice(callback: CallbackQuery):
    await callback.answer()

    gender = callback.data.split("_")[-1]
    voices = await speechify_text_to_speach.get_voices(gender)

    message_text = f'<b>🧍 Здесь предоставлены все доступные голоса выбранного пола:\n<blockquote>{"\n".join([f'{v.title()} {speechify_text_to_speach.voice_languages[v]}' for v in voices])}</blockquote>\nНажмите на кнопку чтобы выбрать голос</b>'

    await callback.message.edit_text(
        message_text, reply_markup=await user_kbs.voices(gender)
    )


@router.callback_query(F.data.startswith("set_voice_"))
async def set_voice(callback: CallbackQuery, user_service: UserService):
    await callback.answer()

    voice_id = callback.data.split("_")[-1]

    await user_service.set_user_voice(callback.from_user.id, voice_id)

    await callback.message.edit_text(
        f"<b>Голос {voice_id.title()} успешно выбран!</b>",
        reply_markup=user_kbs.start_voice,
    )


@router.callback_query(F.data == "input_text")
async def input_text_handler(
    callback: CallbackQuery, state: FSMContext, user_service: UserService
):
    await callback.answer()

    user = await user_service.get(callback.from_user.id)

    await callback.message.answer(
        f"<b>Введите текст для озвучки, который не превышает 2000 символов\n\n<blockquote>1 ⭐️ - 150 символов\nВаш баланс {user.balance}⭐️\nХватит на {user.balance * 150} символов</blockquote></b>",
        reply_markup=user_kbs.back_kb,
    )

    await state.set_state(UserState.text)


@router.message(UserState.text)
async def generate_audio(
    message: Message, state: FSMContext, user_service: UserService
):
    if message.content_type != ContentType.TEXT or len(message.text) >= 2000:
        await message.answer(
            "<b>Не верные входные данные для озвучки, возможно текст длинее 2000 символов, попробуйте еще раз</b>"
        )
        return

    user = await user_service.get(message.from_user.id)

    if len(message.text) > user.balance * 150:
        await message.answer(
            "<b>У вас недостаточно средств для озвучки текста такой длины, пополните баланс</b>",
            reply_markup=user_kbs.dep_kb,
        )
        await state.clear()
        return

    waiting_message = await message.answer("<b>Аудио генерируется...</b>")

    if not user.voice:
        await message.answer(
            "<b>Упс, кажется вы еще не выбрали голос</b>",
            reply_markup=user_kbs.choose_voice_kb,
        )
        await waiting_message.delete()
        await state.clear()
        return

    try:
        amount = -1 * round(len(message.text) / 150) or -1
        audio_path = await speechify_text_to_speach.text_to_speach(
            message.text, user.voice, message.from_user.id
        )
    except:
        await bot.send_message(int(os.getenv('ADMIN_ID')), 'Произошла ошибка в создании аудио')
        await message.answer("<b>Сервис перегружен, попробуйте немного позже</b>")
        await waiting_message.delete()
        await state.clear()
        return

    await waiting_message.delete()

    audio = FSInputFile(audio_path, filename="audio @top_voicer_bot")
    await waiting_message.answer_audio(
        audio,
        caption=f"<b>⚡️ Все готово!\n🗣 Голос: {user.voice.title()}\n⭐️ Потрачено: {abs(amount)}\n\nАудио с вашим текстом сгенерировано, хотите озвучить новый текст?</b>",
        reply_markup=user_kbs.voice_kb,
    )
    
    await user_service.update_balance(message.from_user.id, amount)
    await state.clear()

    await asyncio.to_thread(os.remove, audio_path)


@router.callback_query(F.data == "back")
async def back_handler(
    callback: CallbackQuery, state: FSMContext, user_service: UserService
):
    await callback.answer()

    user = await user_service.get(callback.from_user.id)
    photo = FSInputFile("images/start.jpg")

    await callback.message.answer_photo(
        photo,
        caption=f"<b>👋 Привет, здесь ты можешь озвучить свой текст разными голосами людей\n\nВаш баланс: {user.balance}⭐️\nХватит на: {user.balance * 150} символов\n\n<blockquote>Качественная озвучка\nБыстрая обработка\nНизкие цены (1 ⭐️ - 150 символов)\nОкругление символов по законам математики\nДо 2000 символов за 1 запрос</blockquote>\n\nИспользуй кнопки ниже👇</b>",
        reply_markup=user_kbs.start_kb,
    )
    try:
        await callback.message.delete()
    except:
        pass
    await state.clear()


@router.callback_query(F.data == "back_to_menu")
async def back_handler(callback: CallbackQuery, user_service: UserService):
    await callback.answer()

    user = await user_service.get(callback.from_user.id)

    voice = (
        user.voice.title()
        if user.voice
        else "не выбран\n\nНеобходимо указать голос для озвучки"
    )
    await callback.message.edit_text(
        f"<b>⚡️ Выберите опцию для продолжения\n\nВыбранный голос: {voice}</b>",
        reply_markup=user_kbs.voice_kb,
    )


@router.message()
async def other_message(message: Message):
    await message.answer("<b>Кажется вы ввели не правильную команду</b>")
