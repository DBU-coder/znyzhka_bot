from re import fullmatch

from aiogram.filters import Filter
from aiogram.types import Message


class UrlFilter(Filter):
    PATTERN = r"^(http|https):\/\/({})(\.[\w.-]+)+([\/\w\.-]*)*\/?$"

    def __init__(self, store_domain: str):
        self.store_domain = store_domain

    async def __call__(self, message: Message):
        if message.text:
            return bool(fullmatch(self.PATTERN.format(self.store_domain), message.text))
