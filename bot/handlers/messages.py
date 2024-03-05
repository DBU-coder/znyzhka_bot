from aiogram.utils.markdown import hbold, hide_link, hitalic, hstrikethrough

from bot.keyboards.pagination import Paginator
from database import Product


class Messages:
    ABOUT_BOT = (
        f"🤖 {hbold('Про бота')}\n\nЦей бот використовується для отримання "
        "інформації про знижки в магазинах.\n🛠️ Наразі знаходиться в розробці. "
        "Для початку роботи введіть команду /start. "
    )
    PRODUCTS_NOT_FOUND = "Вибачте, не знайшли жодного продукту 😔"
    ADDED_TO_WATCHLIST = "Додано до списку слідкування 📝"
    ALREADY_IN_WATCHLIST = "Ви вже слідкуєте за цим продуктом 🤩"

    @staticmethod
    def greeting(name: str = "Незнайомець") -> str:
        return f"Вітаю, {name}! 👋\nВиберіть торгівельну мережу."

    @staticmethod
    def category_menu(pagination: Paginator) -> str:
        return f'{hbold("Категорії")}\n{pagination}'

    @staticmethod
    def product_card(product: Product) -> str:
        card = (
            f"{hide_link(product.url)}\n\n{hbold(product.title)}\n"
            f"{hitalic('Стара ціна: ')}{hstrikethrough(str(product.old_price)+'₴')}\n"
            f"{hitalic('Нова ціна: ')}{hbold(str(product.price)+'₴')}\n"
            f"{hitalic('Знижка: ')}-{product.discount_percent}%🔥🔥🔥"
        )
        if product.price_with_card:
            card += f"\n\n{hbold('З картою АТБ')}💳: {hbold(str(product.price_with_card)+'₴')}"
        return card
