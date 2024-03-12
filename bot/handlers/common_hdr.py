from aiogram import Router
from aiogram.filters import or_f
from aiogram.types import Message

from bot.filters import UrlFilter
from bot.handlers.messages import Messages
from database import Database
from parser.watchparser import ATBSingleProductParser

router = Router(name=__name__)


@router.message(
    or_f(
        UrlFilter(store_domain="www.atbmarket"),
        UrlFilter(store_domain="metro.zakaz"),
    )
)
async def add_to_watchlist(message: Message, db: Database) -> None:
    parser = ATBSingleProductParser(url=message.text)  # type: ignore
    parsed_product = await parser.get_product()
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
