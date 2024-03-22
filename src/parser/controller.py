from aiogram import Bot

from src.bot.data_structure import ParsedProduct
from src.bot.handlers.messages import Messages
from src.database import Category, Database
from src.database.models import TrackableProduct

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
    parsed_products = await parse_new_product_data(db)
    for parsed_product in parsed_products:
        trackable_product = await db.trackable_product.get_by_where(
            TrackableProduct.url == parsed_product.url
        )
        if (parsed_product.price is None) != (trackable_product.price is None):  # type: ignore
            out_of_stock = parsed_product.price is None
            await _send_stock_notification(
                bot, trackable_product, parsed_product, out_of_stock  # type: ignore
            )
            await db.trackable_product.update(parsed_product._asdict())
        elif (
            parsed_product.price != trackable_product.price  # type: ignore
            or parsed_product.price_with_card != trackable_product.price_with_card  # type: ignore
        ):
            await _send_change_price_notification(
                bot, trackable_product, parsed_product  # type: ignore
            )
            await db.trackable_product.update(parsed_product._asdict())


async def parse_new_product_data(db: Database) -> list[ParsedProduct]:
    parser = ATBProductParser(urls=await db.trackable_product.get_urls())
    return await parser.get_products()


async def _send_change_price_notification(
    bot: Bot, trackable_product: TrackableProduct, parsed_product: ParsedProduct
):
    users = await trackable_product.awaitable_attrs.users
    await Messages.send_message_to_users(
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
    await Messages.send_message_to_users(bot, users, message)
