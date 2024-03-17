from asyncio import gather
from collections.abc import Iterable
from typing import ClassVar

from fake_useragent import UserAgent
from requests import Response
from requests_html import HTML, AsyncHTMLSession

from bot.data_structure import ParsedCategory, ParsedProduct


class ATBCategoryProductsParser:
    _PRODUCT_PER_PAGE: ClassVar[int] = 36
    _HEADERS: ClassVar[dict[str, str | int]] = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;\
        q=0.8,application/signed-exchange;v=b3;q=0.7"
    }

    def __init__(self, urls: Iterable[str]):
        self.urls = urls
        self._HEADERS["User-Agent"] = UserAgent().random

    @staticmethod
    def _parse_product_data(product_card: HTML, cat_url: str) -> ParsedProduct:
        """Parse product data from given HTML block."""

        title_block = product_card.find(".catalog-item__title", first=True)
        with_card_price = product_card.find("data.atbcard-sale__price-top", first=True)
        product = ParsedProduct(
            title=title_block.text.strip(),
            image=product_card.find("img", first=True).attrs["src"],
            url="https://www.atbmarket.com" + title_block.find("a", first=True).attrs["href"],
            price=float(product_card.find("data.product-price__top", first=True).attrs["value"]),
            old_price=float(product_card.find("data.product-price__bottom", first=True).attrs["value"]),
            discount_percent=int(product_card.find("span.custom-product-label", first=True, containing="%").text[1:-1]),
            price_with_card=float(with_card_price.attrs["value"]) if with_card_price else None,
            cat_url=cat_url,
        )
        return product

    async def _parse_product_cards(self, response: Response) -> list[ParsedProduct]:
        cards = response.html.find("article.catalog-item")  # type: ignore
        page_data = []
        for card in cards:
            discount_block = card.find("span.custom-product-label", first=True, containing="%")
            if discount_block:
                cat_url = response.url.split("&")[0]
                product_data = self._parse_product_data(card, cat_url)
                page_data.append(product_data)
        return page_data

    async def _fetch_page_data(self, session: AsyncHTMLSession, url: str, **params) -> list[ParsedProduct]:
        response = await session.get(url, headers=self._HEADERS, params=params)
        print(url)
        return await self._parse_product_cards(response)

    async def get_data(self):
        session = AsyncHTMLSession()
        tasks = []
        for url in self.urls:
            response = await session.get(url, headers=self._HEADERS)
            pages = self._get_pagination(response)
            if pages > 1:
                for page in range(2, pages + 1):
                    tasks.append(self._fetch_page_data(session, url, params={"page": page}))
            tasks.append(self._parse_product_cards(response))
        pages_data_list = await gather(*tasks)
        all_data = []
        for page_data in pages_data_list:
            all_data.extend(page_data)
        return all_data

    def _get_pagination(self, response: Response) -> int:
        product_quantity = response.html.find("div.product-search-count-bottom", first=True).text.split()[-1]  # type: ignore
        return (int(product_quantity) // self._PRODUCT_PER_PAGE) + 1


class ATBCategoryParser:
    _URL: ClassVar[str] = "https://www.atbmarket.com/promo/sale_tovari"
    _HEADERS: ClassVar[dict[str, str | int]] = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;\
        q=0.8,application/signed-exchange;v=b3;q=0.7"
    }

    def __init__(self):
        self._HEADERS["User-Agent"] = UserAgent().random

    async def get_categories_links(self, session: AsyncHTMLSession) -> list:
        response = await session.get(url=self._URL, headers=self._HEADERS)
        categories = response.html.find("div.catalog-subcategory-list", first=True)
        return list(categories.absolute_links)[:3]

    async def parse_category_products(self, session: AsyncHTMLSession, url: str) -> ParsedCategory:
        response = await session.get(url, headers=self._HEADERS)
        title = response.html.find("span.custom-tag--white-active", first=True).text
        print(title)
        return ParsedCategory(title=title, url=url)

    async def get_data(self):
        session = AsyncHTMLSession()
        links = await self.get_categories_links(session)
        tasks = [self.parse_category_products(session, link) for link in links]
        return await gather(*tasks)
