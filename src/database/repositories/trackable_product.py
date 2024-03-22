from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Product, TrackableProduct
from src.database.repositories.abstract import Repository


class TrackableProductRepository(Repository[TrackableProduct]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=TrackableProduct, session=session)

    async def new(
        self,
        *,
        title: str,
        url: str,
        price: float,
        image: str | None = None,
        old_price: float | None = None,
        discount_percent: int | None = None,
        price_with_card: float | None = None,
    ) -> TrackableProduct:
        new_product = await self.session.merge(
            TrackableProduct(
                title=title,
                image=image,
                url=url,
                price=price,
                old_price=old_price,
                price_with_card=price_with_card,
                discount_percent=discount_percent,
            )
        )
        return new_product

    async def new_from_product(self, product: Product) -> TrackableProduct:
        new_product = await self.session.merge(
            TrackableProduct(
                title=product.title,
                image=product.image,
                url=product.url,
                price=product.price,
                old_price=product.old_price,
                price_with_card=product.price_with_card,
                discount_percent=product.discount_percent,
            )
        )
        return new_product

    async def update(self, data: dict):
        statement = insert(self.type_model).on_conflict_do_update(
            set_=dict(
                price=data["price"],
                price_with_card=data["price_with_card"],
                old_price=data["old_price"],
                discount_percent=data["discount_percent"],
            ),
        )
        await self.session.execute(statement, data)

    async def get_urls(self):
        return await self.session.scalars(select(self.type_model.url))
