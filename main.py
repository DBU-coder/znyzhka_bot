import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.data import database as db
from bot.handlers import router as main_router
from bot.utils.func import check_price

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'), parse_mode='HTML')


async def on_startup():
    await db.create_tables()
    logging.info('DB connected successfully.')
    asyncio.create_task(check_price(bot))


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
