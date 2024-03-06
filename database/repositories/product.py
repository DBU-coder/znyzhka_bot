from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product
from database.repositories.abstract import Repository


class ProductRepository(Repository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Product, session=session)

    async def new(
        self,
        title: str,
        image: str | None,
        url: str,
        price: float,
        old_price: float | None,
        discount_percent: int,
        category_id: int,
        price_with_card: float | None = None,
    ) -> Product:
        new_product = await self.session.merge(
            Product(
                title=title,
                image=image,
                url=url,
                price=price,
                old_price=old_price,
                price_with_card=price_with_card,
                discount_percent=discount_percent,
                category_id=category_id,
            )
        )
        return new_product
