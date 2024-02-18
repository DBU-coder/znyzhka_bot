from re import fullmatch

from aiogram.filters import Filter
from aiogram.types import Message


class UrlFilter(Filter):
    PATTERN = r'^(http|https):\/\/({})(\.[\w.-]+)+([\/\w\.-]*)*\/?$'

    def __init__(self, store_url: str):
        self.store_url = store_url

    async def __call__(self, message: Message):
        return bool(fullmatch(self.PATTERN.format(self.store_url), message.text))
