from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product
from database.repositories.abstract import Repository


class ProductRepository(Repository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Product, session=session)

    async def new(
            self,
            title: str,
            image: Optional[str],
            url: str,
            price: float,
            old_price: Optional[float],
            discount_percent: int,
            category_id: int,
            price_with_card: Optional[float] = None,
            in_wishlist: bool = False
    ) -> Product:
        new_user = await self.session.merge(
            Product(
                title=title,
                image=image,
                url=url,
                price=price,
                old_price=old_price,
                price_with_card=price_with_card,
                discount_percent=discount_percent,
                in_wishlist=in_wishlist,
                category_id=category_id
            )
        )
        return new_user
