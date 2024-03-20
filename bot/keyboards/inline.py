from collections.abc import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database import Category


class WatchlistCallback(CallbackData, prefix="watchlist"):
    action: str
    product_id: int


def get_category_buttons(categories: Sequence[Category]) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            text=category.title[:30], callback_data=f"category_{category.id}"
        )
        for category in categories
    ]


def add_to_watchlist_ikb(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Add to watchlist",
                    callback_data=WatchlistCallback(
                        action="add", product_id=product_id
                    ).pack(),
                )
            ]
        ]
    )


def remove_from_watchlist_ikb(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Remove from watchlist",
                    callback_data=WatchlistCallback(
                        action="remove", product_id=product_id
                    ).pack(),
                )
            ]
        ]
    )
