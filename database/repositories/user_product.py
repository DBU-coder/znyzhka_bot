from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserProduct
from database.repositories.abstract import Repository


class UserProductRepository(Repository[UserProduct]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=UserProduct, session=session)

    async def new(self, user_id: int, product_id: int) -> UserProduct:
        ...

