from aiogram import Bot
from aiogram.utils.markdown import hbold, hide_link, hitalic, hlink, hstrikethrough

from src.bot.data_structure import ParsedProduct
from src.bot.keyboards.pagination import Paginator
from src.database import Product
from src.database.models import TrackableProduct, User


class Messages:
    ABOUT_BOT = (
        f"🤖 {hbold('Про бота')}\n\nЦей бот використовується для отримання "
        "інформації про знижки в магазинах.\n🛠️ Наразі знаходиться в розробці. "
        "Для початку роботи введіть команду /start. "
    )
    PRODUCTS_NOT_FOUND = "Вибачте, не знайшли жодного продукту 😔"
    ADDED_TO_WATCHLIST = "Додано до списку слідкування 📝"
    ALREADY_IN_WATCHLIST = "Ви вже слідкуєте за цим продуктом 🤩"
    EMPTY_WATCHLIST = "Ваш список слідкування 📝 порожній. 😔"
    REMOVED_FROM_WATCHLIST = "Ви вилучили продукт зі списку слідкування 📝"

    @staticmethod
    def greeting(name: str = "Незнайомець") -> str:
        return f"Вітаю, {name}! 👋\nВиберіть торгівельну мережу."

    @staticmethod
    def category_menu(pagination: Paginator) -> str:
        return f'{hbold("Категорії")}\n{pagination}'

    @staticmethod
    def product_card(product: TrackableProduct | Product) -> str:
        card = (
            f"{hide_link(product.url)}\n\n{hbold(product.title)}\n"
            f"{hitalic('Стара ціна: ')}{hstrikethrough(str(product.old_price)+'₴')}\n"
            f"{hitalic('Нова ціна: ')}{hbold(str(product.price)+'₴')}\n"
        )
        if product.price_with_card:
            card += f"\n{hbold('З картою АТБ')}💳: {hbold(str(product.price_with_card)+'₴')}"
        if product.discount_percent:
            card += f"\n{hitalic('Знижка: ')}-{product.discount_percent}%🔥🔥🔥"
        return card

    @staticmethod
    def price_notification(
        trackable_product: TrackableProduct, parsed_product: ParsedProduct
    ) -> str:
        message = (
            f"{'🟢' if parsed_product.price < trackable_product.price or parsed_product.price_with_card else '🔴'}"  # type: ignore
            f"Ціна на {hlink(trackable_product.title, trackable_product.url)} змінилась!\n\n"
            f"{hitalic('Стара ціна: ')}{hstrikethrough(str(trackable_product.price) + '₴')}\n"
            f"{hitalic('Нова ціна: ')}{hbold(str(parsed_product.price)+'₴')}\n"
        )
        if trackable_product.price_with_card and parsed_product.price_with_card:
            message += (
                f"З картою стара💳: {str(trackable_product.price_with_card) + '₴'}\n"
            )
        elif parsed_product.price_with_card:
            message += f"{hbold('З картою')}💳: {hbold(str(parsed_product.price_with_card)+'₴')}\n"
        elif parsed_product.discount_percent:
            message += f"{hitalic('Знижка: ')}-{parsed_product.discount_percent}%🔥🔥🔥"
        return message

    @staticmethod
    def out_of_stock_notification(trackable_product: TrackableProduct) -> str:
        return (
            f"Товар {hlink(trackable_product.title, trackable_product.url)} закінчився!"
        )

    @staticmethod
    def in_stock_notification(
        trackable_product: TrackableProduct, parsed_product: ParsedProduct
    ) -> str:
        message = (
            f"Товар {hlink(trackable_product.title, trackable_product.url)} в наявності!\n\n"
            f"{hitalic('Ціна: ')}{hbold(str(parsed_product.price) + '₴')}"
        )
        if parsed_product.price_with_card:
            message += f"\n{hbold('З картою')}💳: {hbold(str(parsed_product.price_with_card) + '₴')}"
        if parsed_product.discount_percent:
            message += (
                f"\n{hitalic('Знижка: ')}-{parsed_product.discount_percent}%🔥🔥🔥"
            )
        return message

    @staticmethod
    async def send_message_to_users(bot: Bot, users: list[User], message: str):
        for user in users:
            await bot.send_message(user.tg_id, message)
