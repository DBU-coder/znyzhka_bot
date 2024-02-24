import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.data import database as db
from bot.handlers import router as main_router
from bot.utils.func import check_price
from config import configure

bot = Bot(token=configure.bot.token, parse_mode='HTML')


async def on_startup():
    db.create_tables()
    logging.info('DB connected successfully.')
    asyncio.create_task(check_price(bot))


async def starting_bot():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(starting_bot())
