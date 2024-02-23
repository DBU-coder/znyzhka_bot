from typing import Sequence, NamedTuple

from requests import Response

from parser.htmlparser import HTMLParser


class Product(NamedTuple):
    title: str
    price: float
    price_with_card: float | None


class ATBFavoriteProductParser(HTMLParser):
    _URLS = ['https://www.atbmarket.com/product/kava-140g-carte-noire-rozcinna-sublimovana']

    def _parse_product_data(self, response: Response) -> Sequence[dict]:
        price = float(response.html.xpath('//*[@id="productMain"]/div/div[3]/div[1]/data/span', first=True).text)
        with_card_block = response.html.find('data.atbcard-sale__price-top', first=True)
        title = response.html.find('h1.product-page__title', first=True).text
        price_with_card = float(with_card_block.text) if with_card_block else None
        return Product(title, price, price_with_card)
