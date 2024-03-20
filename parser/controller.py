from aiogram import Bot

from bot.data_structure import ParsedProduct
from bot.handlers.messages import Messages
from database import Category, Database
from database.models import TrackableProduct, User

from .atbparser import ATBCategoryParser, ATBCategoryProductsParser
from .watchparser import ATBProductParser


async def parse_category(db: Database) -> None:
    parser = ATBCategoryParser()
    parsed_data = await parser.get_data()
    urls = [category["url"] for category in parsed_data]
    await db.category.delete(Category.url.not_in(urls))
    await db.category.insert(parsed_data)


async def parse_products(db: Database) -> None:
    categories = await db.category.get_many()
    category_urls_to_id = {category.url: category.id for category in categories}
    parser = ATBCategoryProductsParser(category_urls_to_id.keys())
    data = await parser.get_data()
    data_to_insert = [
        {
            "title": item.title,
            "image": item.image,
            "url": item.url,
            "price": item.price,
            "old_price": item.old_price,
            "price_with_card": item.price_with_card,
            "discount_percent": item.discount_percent,
            "category_id": category_urls_to_id[item.cat_url],
        }
        for item in data
    ]
    await db.product.insert(data_to_insert)


async def update_trackable_products(db: Database, bot: Bot):
    trackable_products = await db.trackable_product.get_many()
    urls = [prod.url for prod in trackable_products]
    parser = ATBProductParser(urls)
    parsed_products: list[ParsedProduct] = await parser.get_products()

    for parsed_product in parsed_products:
        trackable_product = await db.trackable_product.get_by_where(
            TrackableProduct.url == parsed_product.url
        )
        if (
            parsed_product.price is None and trackable_product.price is not None  # type: ignore
        ):
            await _send_stock_notification(bot, trackable_product, parsed_product, out_of_stock=True)  # type: ignore
            await db.trackable_product.update(parsed_product._asdict())
        elif (
            trackable_product.price is None and parsed_product.price is not None  # type: ignore
        ):
            await _send_stock_notification(bot, trackable_product, parsed_product, out_of_stock=False)  # type: ignore
            await db.trackable_product.update(parsed_product._asdict())
        elif (
            parsed_product.price != trackable_product.price  # type: ignore
            or parsed_product.price_with_card != trackable_product.price_with_card  # type: ignore
        ):
            await _send_change_price_notification(bot, trackable_product, parsed_product)  # type: ignore
            await db.trackable_product.update(parsed_product._asdict())


async def _send_change_price_notification(
    bot: Bot, trackable_product: TrackableProduct, parsed_product: ParsedProduct
):
    users = await trackable_product.awaitable_attrs.users
    await _send_messages_to_users(
        bot,
        users,
        message=Messages.price_notification(trackable_product, parsed_product),
    )


async def _send_stock_notification(
    bot: Bot,
    trackable_product: TrackableProduct,
    parsed_product: ParsedProduct,
    out_of_stock: bool = False,
):
    users = await trackable_product.awaitable_attrs.users
    if out_of_stock:
        message = Messages.out_of_stock_notification(trackable_product)
    else:
        message = Messages.in_stock_notification(trackable_product, parsed_product)
    await _send_messages_to_users(bot, users, message)


async def _send_messages_to_users(bot: Bot, users: list[User], message: str):
    for user in users:
        await bot.send_message(user.tg_id, message)
