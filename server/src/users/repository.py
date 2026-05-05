from src.kit.repository import BaseRepository, IDRepositoryMixin, Options
from src.models import User


class UserRepository(BaseRepository[User], IDRepositoryMixin[User, int]):
    model = User

    async def get_by_api_key(self, api_key: str) -> User | None:
        return await self.get_one_or_none(
            self.get_base_stmt().where(User.api_key == api_key)
        )

    async def get_by_id_for_update(
        self, id: int, *, nowait: bool = True, options: Options = ()
    ):
        statement = (
            self.get_base_stmt()
            .where(User.id == id)
            .options(*options)
            .with_for_update(nowait=nowait, of=User)
        )
        return await self.get_one_or_none(statement)
