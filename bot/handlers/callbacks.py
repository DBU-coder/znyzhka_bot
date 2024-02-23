from typing import Optional

from aiogram import F, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery

import bot.data.database as db
from parser.atb_parser import parser as atb_parser

router = Router()


class WishlistCallback(CallbackData, prefix='wish'):
    action: str
    product_id: Optional[int] = None
    slug: Optional[str] = None


@router.callback_query(WishlistCallback.filter(F.action == 'add'))
async def add_product_to_wishlist(query: CallbackQuery, callback_data: WishlistCallback):
    url_prefix = 'https://www.atbmarket.com/product/'
    absolute_url = f'{url_prefix}{callback_data.slug}'
    user = db.get_user(query.from_user.id)
    product = db.get_product(url=absolute_url)
    if product:
        product_id = product[0]
    else:
        product_data = await atb_parser.collect_fav_products_info(absolute_url)
        product_id = db.create_product(
            title=product_data.title,
            url=product_data.url,
            price=product_data.price,
            price_with_card=product_data.price_with_card
        )
    db.add_to_wishlist(user_id=user[0], product_id=product_id)
    await query.answer('Product added to your wishlist successfully.')


@router.callback_query(WishlistCallback.filter(F.action == 'delete'))
async def remove_product_from_wishlist(query: CallbackQuery, callback_data: WishlistCallback):
    user = db.get_user(query.from_user.id)
    db.remove_from_wishlist(user_id=user[0], product_id=callback_data.product_id)
    await query.answer('Product removed from your wishlist successfully.')
