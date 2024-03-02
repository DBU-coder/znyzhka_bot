import asyncio

from sqlalchemy import Engine, ForeignKey, String, delete, event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


async def process_scheme(engine: AsyncEngine):
    """Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Base(DeclarativeBase):
    def __repr__(self):
        columns = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
        return f"<{self.__class__.__name__}({', '.join(columns)})>"


class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id", ondelete="CASCADE"))

    category: Mapped["Category"] = relationship(back_populates="products")


async def fill_db(session: AsyncSession):
    category_1 = Category(name="Category 1")
    category_2 = Category(name="Category 2")
    category_3 = Category(name="Category 3")
    product_1 = Product(name="Product 1", category=category_1)
    product_2 = Product(name="Product 2", category=category_2)
    product_3 = Product(name="Product 3", category=category_3)
    product_4 = Product(name="Product 4", category=category_1)
    product_5 = Product(name="Product 5", category=category_2)
    product_6 = Product(name="Product 6", category=category_3)
    session.add_all(
        [category_1, category_2, category_3, product_1, product_2, product_3, product_4, product_5, product_6]
    )


async def delete_category(session: AsyncSession, category_id: int):
    statement = delete(Category).where(Category.id == category_id)
    await session.execute(statement)


async def main():
    engine = create_async_engine("sqlite+aiosqlite:///test.db", echo=True)
    await process_scheme(engine)
    session_maker = async_sessionmaker(engine)
    async with session_maker() as session:
        await fill_db(session)
        await delete_category(session, 2)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
