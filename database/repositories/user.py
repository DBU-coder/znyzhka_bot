from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories.abstract import Repository


class UserRepository(Repository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=User, session=session)

    async def new(
        self,
        user_id: int,
        full_name: str | None = None,
    ) -> User:
        new_user = User(user_id=user_id, full_name=full_name)
        return await self.session.merge(new_user)
