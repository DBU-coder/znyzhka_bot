import logging
from abc import ABC, abstractmethod
from asyncio import gather
from collections.abc import Sequence
from typing import ClassVar

from fake_useragent import UserAgent
from requests import Response
from requests_html import AsyncHTMLSession


class HTMLParser(ABC):
    _URLS: list[str] = []
    _PARAMS: ClassVar[dict[str, str | int]] = {}
    _HEADERS: ClassVar[dict[str, str]] = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;\
        q=0.8,application/signed-exchange;v=b3;q=0.7"
    }

    def __init__(self):
        self._HEADERS["User-Agent"] = UserAgent().random

    @abstractmethod
    def _parse_page_data(self, response: Response) -> Sequence[dict]:
        pass

    async def __fetch_product_data(self, session: AsyncHTMLSession, url: str) -> Sequence[dict]:
        try:
            response = session.get(url, headers=self._HEADERS, params=self._PARAMS)
            return self._parse_page_data(await response)
        except Exception as e:
            logging.exception(f"An error occurred while fetching data from {url}: {e}")
            return []

    async def get_data_from_urls(self) -> Sequence:
        session = AsyncHTMLSession()
        return await gather(*[self.__fetch_product_data(session, url) for url in self._URLS])
