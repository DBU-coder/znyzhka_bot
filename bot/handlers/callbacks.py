from typing import Optional

from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery

import bot.data.database as db

router = Router()


class WishlistCallback(CallbackData, prefix='wish'):
    action: str
    product_id: Optional[int] = None
    slug: Optional[str] = None


@router.callback_query(WishlistCallback.filter(F.action == 'delete'))
async def remove_product_from_wishlist(query: CallbackQuery, callback_data: WishlistCallback):
    user = db.get_user(query.from_user.id)
    db.remove_from_wishlist(user_id=user[0], product_id=callback_data.product_id)
    await query.answer('Product removed from your wishlist successfully.')
