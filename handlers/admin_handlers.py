from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

import os

from database.services.user_service import UserService
from middleware.db_di import DatabaseDI


load_dotenv()

router = Router()
router.message.middleware(DatabaseDI())


@router.message(Command("admin"))
async def admin(message: Message, user_service: UserService):
    if message.from_user.id == int(os.getenv("ADMIN_ID")):
        users = await user_service.get_all()

        await message.answer(
            f"Всего пользователей: {len(users)}\n\nЧтобы выдать баланс пропишите команду <code>/dep user_id amount</code>\nПример: <blockquote>/dep 7648439434 10</blockquote>"
            "\n\nБилинг - https://console.sws.speechify.com/billing"
        )


@router.message(Command("dep"))
async def dep_balance(message: Message, user_service: UserService):
    if message.from_user.id == int(os.getenv("ADMIN_ID")):
        try:
            amount = int(message.text.split()[-1])
            user_id = message.text.split()[1]

            await user_service.update_balance(user_id, amount)
            await message.answer("Успешно")
        except:
            await message.answer("Что-то пошло не так")
