from aiogram.utils.markdown import hbold


class Message:
    ABOUT_BOT = (
        f"🤖 {hbold('Про бота')}\n\nЦей бот використовується для отримання "
        "інформації про знижки в магазинах.\n🛠️ Наразі знаходиться в розробці. "
    )

    @staticmethod
    def greeting(name: str = "Незнайомець") -> str:
        return f"Вітаю, {name}! 👋\nВиберіть торгівельну мережу."
