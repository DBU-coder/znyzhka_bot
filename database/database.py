from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.repositories import (
    CategoryRepository,
    ProductRepository,
    UserProductRepository,
    UserRepository,
)


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
    user_product: UserProductRepository

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user = UserRepository(session=session)
        self.product = ProductRepository(session=session)
        self.category = CategoryRepository(session=session)
        self.user_product = UserProductRepository(session=session)
