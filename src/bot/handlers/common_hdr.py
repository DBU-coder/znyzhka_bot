from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.types import CallbackQuery, Message

from src.bot.filters import UrlFilter
from src.bot.handlers.messages import Messages
from src.bot.keyboards.inline import WatchlistCallback
from src.database import Database
from src.parser.watchparser import ATBProductParser

router = Router(name=__name__)


@router.message(
    or_f(
        UrlFilter(store_domain="www.atbmarket"),
        UrlFilter(store_domain="metro.zakaz"),
    )
)
async def add_to_watchlist(message: Message, db: Database) -> None:
    parser = ATBProductParser(urls=[message.text])  # type: ignore
    parsed_products = await parser.get_products()
    parsed_product = parsed_products[0]
    user = await db.user.get(ident=message.from_user.id)  # type: ignore
    trackable_products = await user.awaitable_attrs.tracks_products  # type: ignore
    trackable_urls = [trackable_product.url for trackable_product in trackable_products]
    if parsed_product.url in trackable_urls:
        await message.answer(Messages.ALREADY_IN_WATCHLIST)
        return

    new_trackable_product, _ = await db.trackable_product.get_or_create(
        title=parsed_product.title,
        url=parsed_product.url,
        old_price=parsed_product.old_price,
        price=parsed_product.price,
        price_with_card=parsed_product.price_with_card,
        discount_percent=parsed_product.discount_percent,
        image=parsed_product.image,
    )
    trackable_products.append(new_trackable_product)
    await message.answer(Messages.ADDED_TO_WATCHLIST)


@router.callback_query(WatchlistCallback.filter(F.action == "remove"))
async def remove_from_watchlist(
    query: CallbackQuery, callback_data: WatchlistCallback, db: Database
):
    await db.user_trackable_product.remove(query.from_user.id, callback_data.product_id)
    await query.answer(text=Messages.REMOVED_FROM_WATCHLIST)
    await query.message.delete()  # type: ignore
