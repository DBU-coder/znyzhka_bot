from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton

from database import Category


def get_category_buttons(categories: Sequence[Category]) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(text=category.title[:30], callback_data=f"category_{category.id}")
        for category in categories
    ]
