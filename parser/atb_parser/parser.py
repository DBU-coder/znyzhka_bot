import asyncio
import json
from typing import NamedTuple

from requests import Response
from requests_html import AsyncHTMLSession

from .config import DATA_FILE, HEADERS, PER_PAGE, URL


class Product(NamedTuple):
    title: str
    url: str
    price: float
    price_with_card: float | None


async def parse_product_data(html_block) -> dict:
    """Parse product data from given HTML block."""
    title_block = html_block.find('.catalog-item__title', first=True)
    product_data = {
        'title': title_block.text.strip(),
        'img': html_block.find('img', first=True).attrs['src'],
        'link': 'https://www.atbmarket.com' + title_block.find('a', first=True).attrs['href'],
        'new_price': float(html_block.find('data.product-price__top', first=True).attrs['value']),
        'old_price': float(html_block.find('data.product-price__bottom', first=True).attrs['value']),
        'discount_percent': int(html_block.find('span.custom-product-label', first=True, containing='%').text[1:-1])
    }
    with_card_price = html_block.find('data.atbcard-sale__price-top', first=True)
    if with_card_price:
        product_data.update(with_card=float(with_card_price.attrs['value']))
    return product_data


async def parse_favorite_product_data(session: AsyncHTMLSession, product_url: str) -> NamedTuple:
    """Parse data for products in wishlist."""
    response = await session.get(product_url, headers=HEADERS)
    price = float(response.html.xpath('//*[@id="productMain"]/div/div[3]/div[1]/data/span', first=True).text)
    with_card_block = response.html.find('data.atbcard-sale__price-top', first=True)
    title = response.html.find('h1.product-page__title', first=True).text
    price_with_card = float(with_card_block.text) if with_card_block else None
    return Product(title, product_url, price, price_with_card)


async def get_page_products(response: Response) -> list[dict]:
    """
    Get product cards and parse product.
    Creates json data from given list of products
    """
    cards = response.html.find('article.catalog-item')
    page_data = []
    for card in cards:
        discount_block = card.find('span.custom-product-label', first=True, containing='%')
        if discount_block:
            product_data = await parse_product_data(card)
            page_data.append(product_data)
    return page_data


async def get_categories_links(session: AsyncHTMLSession) -> list:
    """Returns categories absolute links."""
    response = await session.get(url=URL, headers=HEADERS)
    categories = response.html.find('div.catalog-subcategory-list', first=True)
    return categories.absolute_links


async def parse_category_products(session: AsyncHTMLSession, cat_url: str) -> dict:
    """Returns category data with products list."""
    response = await session.get(url=cat_url, headers=HEADERS)
    name = response.html.find('span.custom-tag--white-active', first=True).text
    quantity = int(response.html.find('div.product-search-count-bottom', first=True).text.split()[-1])
    pages = (quantity // PER_PAGE) + 1
    products = await get_page_products(response)
    if pages > 1:
        for page in range(2, pages + 1):
            response = await session.get(url=cat_url, headers=HEADERS, params={'page': page})
            page_products = await get_page_products(response)
            products.extend(page_products)
    return {'name': name, 'link': cat_url, 'quantity': quantity, 'products': products}


async def create_category_tasks():
    s = AsyncHTMLSession()
    links = await get_categories_links(s)
    tasks = [parse_category_products(s, link) for link in links]
    return await asyncio.gather(*tasks)


async def create_product_data_tasks(links: list):
    s = AsyncHTMLSession()
    tasks = [parse_favorite_product_data(s, link) for link in links]
    return await asyncio.gather(*tasks)


async def collect_price(links: list):
    loop = asyncio.get_event_loop()
    tasks = create_product_data_tasks(links)
    result = await loop.create_task(tasks)
    return result


async def collect_cat_info() -> None:
    loop = asyncio.get_event_loop()
    tasks = create_category_tasks()
    results = await loop.create_task(tasks)
    results.sort(key=lambda x: x['name'])
    with open(DATA_FILE, 'w') as file:
        json.dump(results, file, indent=4, ensure_ascii=False)


async def collect_fav_products_info(url):
    loop = asyncio.get_event_loop()
    s = AsyncHTMLSession()
    result = await loop.create_task(parse_favorite_product_data(s, url))
    return result
