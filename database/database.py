from sqlalchemy import URL, Engine, event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.repositories import CategoryRepository, ProductRepository, UserRepository


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    """
    Enable foreign key support in SQLite.
    https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#sqlite-foreign-keys
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_engine(url: URL | str) -> AsyncEngine:
    return create_async_engine(
        url=url,
        echo=True,
    )


def create_session_maker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(engine)


class Database:
    session: AsyncSession
    user: UserRepository
    product: ProductRepository
    category: CategoryRepository

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user = UserRepository(session=session)
        self.product = ProductRepository(session=session)
        self.category = CategoryRepository(session=session)
