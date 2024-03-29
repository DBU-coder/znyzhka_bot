from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def select_store_kb(**kwargs) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="ATB"),
        KeyboardButton(text="METRO"),
        KeyboardButton(text="Silpo"),
        KeyboardButton(text="Обрані товари"),
    )
    builder.adjust(3, 1)
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Назва мережі", **kwargs
    )
