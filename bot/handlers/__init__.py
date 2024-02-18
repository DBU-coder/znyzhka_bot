__all__ = ('router',)

from aiogram import Router

from .atb import router as atb_router
from .callbacks import router as callbacks_router
from .commands import router as commands_router
from .common import router as common_router

router = Router(name=__name__)
router.include_routers(
    commands_router,
    atb_router,
    callbacks_router
)
# This one will be last router!
router.include_router(common_router)
