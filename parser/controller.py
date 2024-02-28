from atbparser import ATBCategoryParser, ATBProductParser

from database import Database


async def parse_category(db: Database) -> None:
    parser = ATBCategoryParser()
    parsed_data = await parser.get_data()
    await db.category.insert(parsed_data)


async def parse_products(db: Database) -> None:
    categories = await db.category.get_many()
    cat_urls_to_id = {category.url: category.id for category in categories}
    parser = ATBProductParser([item.url for item in categories])
    data = await parser.get_data()
    data_to_db = [
        {
            "title": item.title,
            "image": item.image,
            "url": item.url,
            "price": item.price,
            "old_price": item.old_price,
            "price_with_card": item.price_with_card,
            "discount_percent": item.discount_percent,
            "in_wishlist": False,
            "category_id": cat_urls_to_id[item.cat_url],
        }
        for item in data
    ]
    await db.product.insert(data_to_db)