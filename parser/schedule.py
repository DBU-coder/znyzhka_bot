import asyncio

import aiojobs
from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker

from database import Database
from parser.controller import parse_category, parse_products


async def checking_discounts(session_maker: async_sessionmaker) -> None:
    time_interval = 24 * 60 * 60
    while True:
        logger.info("Scheduler checks new discounts")
        async with session_maker() as session:
            db = Database(session)
            await parse_category(db)
            await parse_products(db)
            await session.commit()
        await asyncio.sleep(time_interval)


async def start_parser_schedule(session_maker: async_sessionmaker) -> None:
    scheduler = aiojobs.Scheduler()
    await scheduler.spawn(checking_discounts(session_maker))
