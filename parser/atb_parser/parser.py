import asyncio
import json

from requests import Response
from requests_html import AsyncHTMLSession

from .config import DATA_FILE, HEADERS, PER_PAGE, URL


async def parse_product_data(html_block) -> dict:
    """Parse product data from given HTML block."""
    title_block = html_block.find(".catalog-item__title", first=True)
    product_data = {
        "title": title_block.text.strip(),
        "img": html_block.find("img", first=True).attrs["src"],
        "link": "https://www.atbmarket.com" + title_block.find("a", first=True).attrs["href"],
        "new_price": float(html_block.find("data.product-price__top", first=True).attrs["value"]),
        "old_price": float(html_block.find("data.product-price__bottom", first=True).attrs["value"]),
        "discount_percent": int(html_block.find("span.custom-product-label", first=True, containing="%").text[1:-1]),
    }
    with_card_price = html_block.find("data.atbcard-sale__price-top", first=True)
    if with_card_price:
        product_data.update(with_card=float(with_card_price.attrs["value"]))
    return product_data


async def get_page_products(response: Response) -> list[dict]:
    """
    Get product cards and parse product.
    Creates json data from given list of products
    """
    cards = response.html.find("article.catalog-item")
    page_data = []
    for card in cards:
        discount_block = card.find("span.custom-product-label", first=True, containing="%")
        if discount_block:
            product_data = await parse_product_data(card)
            page_data.append(product_data)
    return page_data


async def get_categories_links(session: AsyncHTMLSession) -> list:
    """Returns categories absolute links."""
    response = await session.get(url=URL, headers=HEADERS)
    categories = response.html.find("div.catalog-subcategory-list", first=True)
    return categories.absolute_links


async def parse_category_products(session: AsyncHTMLSession, cat_url: str) -> dict:
    """Returns category data with products list."""
    response = await session.get(url=cat_url, headers=HEADERS)
    name = response.html.find("span.custom-tag--white-active", first=True).text
    quantity = int(response.html.find("div.product-search-count-bottom", first=True).text.split()[-1])
    pages = (quantity // PER_PAGE) + 1
    products = await get_page_products(response)
    if pages > 1:
        for page in range(2, pages + 1):
            response = await session.get(url=cat_url, headers=HEADERS, params={"page": page})
            page_products = await get_page_products(response)
            products.extend(page_products)
    return {"name": name, "link": cat_url, "quantity": quantity, "products": products}


async def create_category_tasks():
    s = AsyncHTMLSession()
    links = await get_categories_links(s)
    tasks = [parse_category_products(s, link) for link in links]
    return await asyncio.gather(*tasks)


async def collect_cat_info() -> None:
    loop = asyncio.get_event_loop()
    tasks = create_category_tasks()
    results = await loop.create_task(tasks)
    results.sort(key=lambda x: x["name"])
    with open(DATA_FILE, "w") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)
