from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


async def process_scheme(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


# declarative base class
class BaseModel(DeclarativeBase):
    pass


class User(BaseModel):
    __tablename__ = 'user'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(64), nullable=True)

    products: Mapped[list['UserProduct']] = relationship(back_populates='user')

    def __repr__(self) -> str:
        return f'User({self.user_id=} {self.full_name=})'


class Product(BaseModel):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    image: Mapped[str] = mapped_column(nullable=True)
    url: Mapped[str] = mapped_column(unique=True)
    price: Mapped[float]
    old_price: Mapped[float] = mapped_column(nullable=True)
    price_with_card: Mapped[float] = mapped_column(nullable=True)
    discount_percent: Mapped[int]
    in_wishlist: Mapped[bool] = mapped_column(default=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'))

    category: Mapped['Category'] = relationship(back_populates='products')

    def __repr__(self):
        return f'Product({self.id=} {self.title=} {self.price} {self.category_id=})'


class Category(BaseModel):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(unique=True)

    products: Mapped[list[Product]] = relationship(back_populates='category')

    def __repr__(self):
        return f'Category({self.id=} {self.title=})'


class UserProduct(BaseModel):
    __tablename__ = 'user_product'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id'))
    user: Mapped[list[Product]] = relationship(back_populates='products')

    def __repr__(self):
        return f'UserProduct({self.id=} {self.user_id=} {self.product_id=})'
