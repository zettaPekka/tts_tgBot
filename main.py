import asyncio
from aiogram import Dispatcher

from init_bot import bot
from handlers.user_handlers import router as user_router
from handlers.payment_handlers import router as payment_router
from handlers.admin_handlers import router as admin_router
from database.database import init_db

import logging


async def main():
    logging.basicConfig(level=logging.INFO)

    await init_db()

    await bot.delete_webhook(drop_pending_updates=True)

    dp = Dispatcher()
    dp.include_routers(admin_router, payment_router, user_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
