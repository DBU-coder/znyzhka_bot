from aiogram import Dispatcher

from bot.middlewares import DatabaseMiddleware, RegisterUserMiddleware
from .atb import router as atb_router
from .callbacks import router as callbacks_router
from .commands import router as commands_router
from .common import router as common_router


def register_handlers(dp: Dispatcher) -> None:
    dp.message.middleware(DatabaseMiddleware)
    dp.message.middleware(RegisterUserMiddleware)
    dp.callback_query.middleware(DatabaseMiddleware)
    dp.callback_query.middleware(RegisterUserMiddleware)
    dp.include_routers(commands_router, atb_router, callbacks_router)
    # This one will be last router!
    dp.include_router(common_router)
