from typing import Annotated, ClassVar

from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Custom types
str_256 = Annotated[str, 256]
intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
str_unique = Annotated[str, mapped_column(unique=True)]


async def process_scheme(engine: AsyncEngine):
    """
    Create all tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


# declarative base class
class BaseModel(AsyncAttrs, DeclarativeBase):
    # Add custom types
    type_annotation_map: ClassVar[dict] = {
        str_256: String(256),
    }

    def __repr__(self):
        columns = [
            f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()
        ]
        return f"<{self.__class__.__name__}({', '.join(columns)})>"


class User(BaseModel):
    __tablename__ = "user"

    tg_id: Mapped[intpk]
    full_name: Mapped[str_256 | None]

    tracks_products: Mapped[list["TrackableProduct"]] = relationship(
        secondary="user_trackable_product", back_populates="users"
    )


class Product(BaseModel):
    __tablename__ = "product"

    id: Mapped[intpk]
    title: Mapped[str_256]
    image: Mapped[str | None]
    url: Mapped[str_unique]
    price: Mapped[float | None]
    old_price: Mapped[float | None]
    price_with_card: Mapped[float | None]
    discount_percent: Mapped[int | None]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id", ondelete="CASCADE")
    )

    category: Mapped["Category"] = relationship(back_populates="products")


class TrackableProduct(BaseModel):
    __tablename__ = "trackable_product"

    id: Mapped[intpk]
    title: Mapped[str_256]
    image: Mapped[str | None]
    url: Mapped[str_unique]
    price: Mapped[float | None]
    old_price: Mapped[float | None]
    price_with_card: Mapped[float | None]
    discount_percent: Mapped[int | None]

    users: Mapped[list[User]] = relationship(
        secondary="user_trackable_product", back_populates="tracks_products"
    )


class Category(BaseModel):
    __tablename__ = "category"

    id: Mapped[intpk]
    title: Mapped[str_256]
    url: Mapped[str_unique]

    products: Mapped[list[Product]] = relationship(
        back_populates="category", cascade="all, delete", passive_deletes=True
    )


class UserTrackableProduct(BaseModel):
    __tablename__ = "user_trackable_product"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.tg_id", ondelete="CASCADE"), primary_key=True
    )
    trackable_product_id: Mapped[int] = mapped_column(
        ForeignKey("trackable_product.id", ondelete="CASCADE"), primary_key=True
    )
