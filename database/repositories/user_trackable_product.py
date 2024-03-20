from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import TrackableProduct, UserTrackableProduct
from database.repositories.abstract import Repository


class UserTrackableProductRepository(Repository[UserTrackableProduct]):

    def __init__(self, session: AsyncSession):
        super().__init__(type_model=UserTrackableProduct, session=session)

    async def new(self, user_id: int, product_id: int):
        await self.session.merge(
            UserTrackableProduct(user_id=user_id, trackable_product_id=product_id)
        )

    async def remove(self, user_id: int, product_id: int):
        await self.delete(
            and_(
                UserTrackableProduct.user_id == user_id,
                UserTrackableProduct.trackable_product_id == product_id,
            )
        )
        await self.__delete_unused()

    async def __delete_unused(self):
        stmt = delete(TrackableProduct).where(
            TrackableProduct.id.not_in(
                select(UserTrackableProduct.trackable_product_id).scalar_subquery()
            )
        )
        await self.session.execute(stmt)

    async def remove_all(self, user_id: int):
        await self.delete(UserTrackableProduct.user_id == user_id)
