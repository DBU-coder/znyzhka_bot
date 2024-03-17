from aiogram import Bot
from aiogram.utils.markdown import hbold, hitalic, hlink, hstrikethrough

from bot.data_structure import ParsedProduct
from database import Category, Database
from database.models import TrackableProduct

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
    db_products = await db.trackable_product.get_many()
    urls = [product.url for product in db_products]
    parser = ATBProductParser(urls)
    parsed_products = await parser.get_products()

    for parsed_product in parsed_products:
        db_product = await db.trackable_product.get_by_where(TrackableProduct.url == parsed_product.url)
        if parsed_product.price != db_product.price or parsed_product.price_with_card != db_product.price_with_card:  # type: ignore
            await _send_change_price_notification(bot, db_product, parsed_product)  # type: ignore
            await db.trackable_product.update(parsed_product._asdict())


async def _send_change_price_notification(bot: Bot, db_product: TrackableProduct, parsed_product: ParsedProduct):
    users = await db_product.awaitable_attrs.users
    message = (
        f"{'🟢' if parsed_product.price < db_product.price or parsed_product.price_with_card else '🔴'}"
        f"Ціна на {hlink(db_product.title, db_product.url)} змінилась!\n\n"
        f"{hitalic('Стара ціна: ')}{hstrikethrough(str(db_product.price)+'₴')}\n"
        f"{hitalic('Нова ціна: ')}{hbold(str(parsed_product.price)+'₴')}\n"
    )
    if db_product.price_with_card and parsed_product.price_with_card:
        message += f"З картою стара💳: {str(db_product.price_with_card)+'₴'}\n"
    elif parsed_product.price_with_card:
        message += f"{hbold('З картою')}💳: {hbold(str(parsed_product.price_with_card)+'₴')}\n"
    elif parsed_product.discount_percent:
        message += f"{hitalic('Знижка: ')}-{parsed_product.discount_percent}%🔥🔥🔥"

    for user in users:
        await bot.send_message(user.tg_id, message)
