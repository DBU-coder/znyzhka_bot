from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.database.repositories import (
    CategoryRepository,
    ProductRepository,
    UserRepository,
)
from src.database.repositories.trackable_product import TrackableProductRepository
from src.database.repositories.user_trackable_product import (
    UserTrackableProductRepository,
)


def create_engine(url: URL | str) -> AsyncEngine:
    return create_async_engine(
        url=url,
        echo=False,
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
        self.trackable_product = TrackableProductRepository(session=session)
        self.user_trackable_product = UserTrackableProductRepository(session=session)
