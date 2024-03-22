from aiogram import Dispatcher
from aiogram.types import BotCommand

from src.bot.middlewares import DatabaseMiddleware, RegisterUserMiddleware

from .atb_hdr import router as atb_router
from .commands_hdr import router as commands_router
from .common_hdr import router as common_router

bot_commands = [
    BotCommand(command="/start", description="Початок роботи з ботом"),
    BotCommand(command="/watchlist", description="Переглянути список обраних товарів"),
    BotCommand(command="/help", description="Допомога"),
]


def register_handlers(dp: Dispatcher) -> None:
    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(RegisterUserMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(RegisterUserMiddleware())
    dp.include_routers(commands_router, atb_router, common_router)
