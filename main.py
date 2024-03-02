import asyncio

from aiogram import Bot, Dispatcher
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.data_structure import ContextData
from bot.handlers.controller import register_handlers
from config import configure
from database import create_engine, create_session_maker
from database.models import process_scheme
from parser.schedule import start_parser_schedule


async def set_up_parser(session_maker: async_sessionmaker) -> None:
    await start_parser_schedule(session_maker)


async def starting_bot():

    # Dispatcher
    bot = Bot(token=configure.bot.token, parse_mode="HTML")
    dp = Dispatcher()
    register_handlers(dp)
    logger.info("Bot starts")

    # Database
    db_url = configure.db.build_connection_url()
    engine = create_engine(db_url)
    session_maker = create_session_maker(engine)
    await process_scheme(engine)
    await set_up_parser(session_maker)

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
        **ContextData(pool=session_maker),  # type: ignore
    )


if __name__ == "__main__":
    try:
        asyncio.run(starting_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
        raise
