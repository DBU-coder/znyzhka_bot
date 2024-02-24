from sqlalchemy import Integer, String, ForeignKey, BigInteger, Float, Boolean
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


async def process_scheme(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


# declarative base class
class BaseModel(DeclarativeBase):
    pass


class User(BaseModel):
    __tablename__ = 'user'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(64), nullable=True)

    products: Mapped[list['UserProduct']] = relationship(back_populates='user')



    def __repr__(self) -> str:
        return f'User({self.user_id=} {self.full_name=})'


class Product(BaseModel):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    old_price: Mapped[float] = mapped_column(Float, nullable=True)
    price_with_card: Mapped[float] = mapped_column(Float, nullable=True)
    discount_percent: Mapped[int] = mapped_column(Integer)
    in_wishlist: Mapped[bool] = mapped_column(Boolean, default=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('category.id'), nullable=False)

    category: Mapped['Category'] = relationship(back_populates='products')

    def __repr__(self):
        return f'Product({self.id=} {self.title=} {self.price} {self.category_id=})'


class Category(BaseModel):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    products: Mapped[list[Product]] = relationship(back_populates='category')

    def __repr__(self):
        return f'Category({self.id=} {self.title=})'


class UserProduct(BaseModel):
    __tablename__ = 'user_product'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id'), nullable=False)
    user: Mapped[list[Product]] = relationship(back_populates='products')

    def __repr__(self):
        return f'UserProduct({self.id=} {self.user_id=} {self.product_id=})'
