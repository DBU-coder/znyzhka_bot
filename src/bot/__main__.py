import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.bot.data_structure import ContextData
from src.bot.handlers.controller import bot_commands, register_handlers
from src.config import configure
from src.database import create_engine, create_session_maker
from src.database.models import process_scheme
from src.parser.schedule import start_parser_schedule


async def set_up_parser(session_maker: async_sessionmaker, bot) -> None:
    await start_parser_schedule(session_maker, bot)


async def starting_bot():

    # Bot
    bot = Bot(
        token=configure.bot.token,
        default=DefaultBotProperties(parse_mode="HTML", disable_notification=True),
    )
    await bot.set_my_commands(bot_commands)

    # Dispatcher
    dp = Dispatcher()
    register_handlers(dp)
    logger.info("Bot starts")

    # Database
    db_url = configure.db.build_connection_url()
    engine = create_engine(db_url)
    session_maker = create_session_maker(engine)
    await process_scheme(engine)
    await set_up_parser(session_maker, bot)

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
