from src.kit.repository import BaseRepository, Options, RepositoryIDMixin
from src.models import User


class UserRepository(RepositoryIDMixin[User, int], BaseRepository[User]):
    model = User

    async def get_by_id_for_update(
        self, id: int, *, nowait: bool = True, options: Options = ()
    ) -> User | None:
        statement = (
            self.get_base_stmt()
            .where(User.id == id)
            .options(*options)
            .with_for_update(nowait=nowait, of=User)
        )
        return await self.get_one_or_none(statement)

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_one_or_none(
            self.get_base_stmt().where(User.username == username)
        )
