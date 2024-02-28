from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserProduct
from database.repositories.abstract import Repository


class UserProductRepository(Repository[UserProduct]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=UserProduct, session=session)

    async def new(self, user_id: int, product_id: int) -> UserProduct:
        existing_record = await self.get_by_where(
            and_(UserProduct.user_id == user_id, UserProduct.product_id == product_id)
        )
        if existing_record:
            await self.delete(UserProduct.id == existing_record.id)
        return await self.session.merge(UserProduct(user_id=user_id, product_id=product_id))
