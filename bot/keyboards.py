from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_choice_store_kb(**kwargs) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="ATB"),
        KeyboardButton(text="METRO"),
        KeyboardButton(text="Silpo"),
        KeyboardButton(text="Обрані товари"),
    )
    builder.adjust(3, 1)
    return builder.as_markup(resize_keyboard=True, **kwargs)
