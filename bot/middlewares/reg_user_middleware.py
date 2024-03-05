from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database import User


class RegisterUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        db = data["db"]
        user_id = event.from_user.id  # type: ignore
        full_name = event.from_user.full_name  # type: ignore
        if not (await db.user.get_by_where(User.tg_id == user_id)):
            await db.user.new(tg_id=user_id, full_name=full_name)
        return await handler(event, data)
