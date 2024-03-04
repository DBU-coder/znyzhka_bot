from aiogram.utils.markdown import hbold

from bot.keyboards.pagination import Paginator


class Messages:
    ABOUT_BOT = (
        f"🤖 {hbold('Про бота')}\n\nЦей бот використовується для отримання "
        "інформації про знижки в магазинах.\n🛠️ Наразі знаходиться в розробці. "
        "Для початку роботи введіть команду /start. "
    )

    @staticmethod
    def greeting(name: str = "Незнайомець") -> str:
        return f"Вітаю, {name}! 👋\nВиберіть торгівельну мережу."

    @staticmethod
    def category_menu(pagination: Paginator) -> str:
        return f'{hbold("Категорії")}\n{pagination}'
