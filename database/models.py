from typing import Annotated, ClassVar

from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Custom types
str_256 = Annotated[str, 256]
intpk = Annotated[int, mapped_column(primary_key=True)]
str_unique = Annotated[str, mapped_column(unique=True)]


async def process_scheme(engine: AsyncEngine):
    """
    Create all tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


# declarative base class
class BaseModel(DeclarativeBase):
    # Add custom types
    type_annotation_map: ClassVar[dict] = {
        str_256: String(256),
    }

    def __repr__(self):
        columns = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
        return f"<{self.__class__.__name__}({', '.join(columns)})>"


class User(BaseModel):
    __tablename__ = "user"

    user_id: Mapped[intpk]
    full_name: Mapped[str_256 | None]

    liked_products: Mapped[list["Product"]] = relationship(secondary="user_product", back_populates="users_liked")


class Product(BaseModel):
    __tablename__ = "product"

    id: Mapped[intpk]
    title: Mapped[str_256]
    image: Mapped[str | None]
    url: Mapped[str_unique]
    price: Mapped[float]
    old_price: Mapped[float | None]
    price_with_card: Mapped[float | None]
    discount_percent: Mapped[int]
    in_wishlist: Mapped[bool] = mapped_column(default=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id", ondelete="CASCADE"))

    category: Mapped["Category"] = relationship(back_populates="products")
    users_liked: Mapped[list[User]] = relationship(secondary="user_product", back_populates="liked_products")


class Category(BaseModel):
    __tablename__ = "category"

    id: Mapped[intpk]
    title: Mapped[str_256]
    url: Mapped[str_unique]

    products: Mapped[list[Product]] = relationship(
        back_populates="category", cascade="all, delete", passive_deletes=True
    )


class UserProduct(BaseModel):
    __tablename__ = "user_product"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id", ondelete="CASCADE"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"), primary_key=True)
