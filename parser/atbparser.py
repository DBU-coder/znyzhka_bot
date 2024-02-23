from typing import Sequence, NamedTuple

from requests import Response

from parser.htmlparser import HTMLParser


class Product(NamedTuple):
    title: str
    url: str
    price: float
    price_with_card: float | None


class ATBFavoriteProductParser(HTMLParser):

    def __init__(self, urls: Sequence[str]):
        super().__init__(urls)

    def _parse_product_data(self, response: Response) -> Product:
        title = response.html.find('h1.product-page__title', first=True).text
        price = float(response.html.xpath('//*[@id="productMain"]/div/div[3]/div[1]/data/span', first=True).text)
        with_card_block = response.html.find('data.atbcard-sale__price-top', first=True)
        price_with_card = float(with_card_block.text) if with_card_block else None
        url = response.url
        return Product(title, url, price, price_with_card)
