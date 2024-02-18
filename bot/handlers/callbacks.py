from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery

import bot.data.database as db

router = Router()


class WishlistCallback(CallbackData, prefix='wish'):
    product_id: int
    action: str


@router.callback_query(WishlistCallback.filter(F.action == 'delete'))
async def remove_product_from_wishlist(query: CallbackQuery, callback_data: WishlistCallback):
    await db.remove_from_wishlist(callback_data.product_id)
    await query.answer('Product removed from your wishlist successfully.')
