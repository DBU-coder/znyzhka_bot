from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Category
from src.database.repositories.abstract import Repository


class CategoryRepository(Repository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Category, session=session)

    async def new(self, title: str, url: str) -> Category:
        new_category = await self.session.merge(Category(title=title, url=url))
        return new_category
