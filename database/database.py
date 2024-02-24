from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from config import configure


def create_engine(url: URL | str) -> AsyncEngine:
    return create_async_engine(
        url=url,
        echo=True,
    )


if __name__ == '__main__':
    # create_engine('sqlite+aiosqlite:///bot_database.db')
    print(configure.db.build_connection_url())
