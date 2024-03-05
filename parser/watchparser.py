import asyncio
from abc import ABC, abstractmethod
from typing import ClassVar

from fake_useragent import UserAgent
from requests import Response
from requests_html import HTML, AsyncHTMLSession

from bot.data_structure import ParsedProduct


class BaseSingleProductParser(ABC):
    _HEADERS: ClassVar[dict[str, str | int]] = {
        "Accept": "text/html,application/xhtml+xml,application/xml;\
            q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }
    url: str = ""

    def __new__(cls, *args, **kwargs):
        cls._HEADERS["User-Agent"] = UserAgent().random
        return super().__new__(cls)

    @staticmethod
    @abstractmethod
    async def _parse_product(response: Response) -> ParsedProduct: ...

    async def __get_product_data(self):
        session = AsyncHTMLSession()
        response = await session.get(self.url, headers=self._HEADERS)
        return await self._parse_product(response)

    async def get_product(self):
        return await asyncio.create_task(self.__get_product_data())


class ATBSingleProductParser(BaseSingleProductParser):

    def __init__(self, url: str):
        self.url = url

    @staticmethod
    async def _parse_product(response: Response) -> ParsedProduct:
        page: HTML = response.html  # type: ignore
        __price_block = page.find("div.product-about__buy-row", first=True)
        old_price_block = __price_block.find("data.product-price__bottom", first=True)
        price_with_card_block = __price_block.find("data.atbcard-sale__price-top", first=True)
        discount_percent_block = page.find("div.product-about__labels", first=True).find(
            "span", first=True, containing="%"
        )

        product = ParsedProduct(
            title=page.find("h1.page-title", first=True).text,
            image=page.find("div.cardproduct-tabs__item", first=True).find("img", first=True).attrs["src"],
            url=response.url,
            price=float(page.find("data.product-price__top", first=True).find("span", first=True).text),
            old_price=float(old_price_block.text) if old_price_block else None,
            price_with_card=float(price_with_card_block.attrs["value"]) if price_with_card_block else None,
            discount_percent=int(discount_percent_block.text[1:-1]) if discount_percent_block else None,
            cat_url=None,
        )
        return product
