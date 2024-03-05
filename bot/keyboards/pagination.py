from math import ceil

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NavigationCallback(CallbackData, prefix="navigation"):
    action: str
    direction: str


class Paginator:
    def __init__(self, buttons: list[InlineKeyboardButton] | None = None, buttons_on_page: int = 3) -> None:
        self.buttons = buttons or []
        self.__buttons_on_page = buttons_on_page
        self.__current_page = 0

    async def update_kb(self) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        from_ = self.__current_page * self.__buttons_on_page
        to_ = (self.__current_page + 1) * self.__buttons_on_page
        builder.add(*[button for button in self.buttons[from_:to_]])
        builder.adjust(1, repeat=True)

        prev_button = InlineKeyboardButton(
            text="<", callback_data=NavigationCallback(action="navigate", direction="previous").pack()
        )
        next_button = InlineKeyboardButton(
            text=">", callback_data=NavigationCallback(action="navigate", direction="next").pack()
        )
        current_page = InlineKeyboardButton(
            text=f"{self.__current_page + 1}/{self.__total_pages()}",
            callback_data=NavigationCallback(action="navigate", direction="first").pack(),
        )

        if from_ <= 0:
            builder.row(current_page, next_button)
            return builder.as_markup()
        elif to_ >= len(self.buttons):
            builder.row(prev_button, current_page)
            return builder.as_markup()

        builder.row(prev_button, current_page, next_button)
        return builder.as_markup()

    async def on_next(self) -> None:
        self.__current_page += 1

    async def on_prev(self) -> None:
        self.__current_page -= 1

    async def on_first(self) -> None:
        self.__current_page = 0

    def __total_pages(self) -> int:
        return ceil(len(self.buttons) / self.__buttons_on_page)

    def __str__(self):
        return f"{self.__current_page + 1}/{self.__total_pages()}"
