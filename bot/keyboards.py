from aiogram.types import (InlineKeyboardMarkup, KeyboardButton,
                           ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.handlers.callbacks import WishlistCallback


def get_choice_store_kb(**kwargs) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text='ATB'),
        KeyboardButton(text='METRO'),
        KeyboardButton(text='Silpo'),
        KeyboardButton(text='Обрані товари'),
    )
    builder.adjust(3, 1)
    return builder.as_markup(resize_keyboard=True, **kwargs)


def get_delete_from_wishlist_ikb(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Видалити з Обраного', callback_data=WishlistCallback(product_id=product_id, action='delete'))
    return builder.as_markup()


