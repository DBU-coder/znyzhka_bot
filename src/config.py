from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()


@dataclass
class DatabaseConfig:
    database_system: str = "postgresql"
    driver: str = "asyncpg"

    database: str | None = getenv("POSTGRES_DB")
    user: str | None = getenv("POSTGRES_USER")
    password: str | None = getenv("POSTGRES_PASSWORD")
    host: str = getenv("POSTGRES_HOST", "localhost")
    port: int = int(getenv("POSTGRES_PORT", "5432"))

    def build_connection_url(self) -> str:
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            username=self.user,
            database=self.database,
            password=self.password,
            port=self.port,
            host=self.host,
        ).render_as_string(hide_password=False)


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
