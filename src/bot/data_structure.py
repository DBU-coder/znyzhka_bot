from collections.abc import Callable
from typing import NamedTuple, TypedDict

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Database


class ContextData(TypedDict):
    pool: Callable[[], AsyncSession]
    db: Database


class ParsedProduct(NamedTuple):
    title: str
    image: str | None
    url: str
    price: float | None
    old_price: float | None
    price_with_card: float | None
    discount_percent: int | None
    cat_url: str | None = None


class ParsedCategory(TypedDict):
    title: str
    url: str
