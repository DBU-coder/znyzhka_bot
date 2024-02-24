from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()


@dataclass
class DatabaseConfig:
    database: str | None = getenv("SQLITE_DB")
    database_system: str = "sqlite"
    driver: str = "aiosqlite"

    def build_connection_url(self) -> str:
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            database=self.database,
        ).render_as_string()


@dataclass
class BotConfig:
    token: str = getenv("BOT_TOKEN", "")
    atb_site: str = "https://www.atbmarket.com"
    atb_sales_url: str = "https://www.atbmarket.com/promo/sale_tovari"


@dataclass
class Config:
    db = DatabaseConfig()
    bot = BotConfig()


configure = Config()
