from database import Category, Database

from .atbparser import ATBCategoryParser, ATBProductParser


async def parse_category(db: Database) -> None:
    parser = ATBCategoryParser()
    parsed_data = await parser.get_data()
    urls = [category["url"] for category in parsed_data]
    await db.category.delete(Category.url.not_in(urls))
    await db.category.insert(parsed_data)


async def parse_products(db: Database) -> None:
    categories = await db.category.get_many()
    category_urls_to_id = {category.url: category.id for category in categories}
    parser = ATBProductParser(category_urls_to_id.keys())
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
