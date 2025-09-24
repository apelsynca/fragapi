from src.exceptions import ResourceNotFound
from src.kit.utils import generate_api_key
from src.logging import get_logger
from src.models import User
from src.users.schemas import UserCreate

from .repository import UserRepository

log = get_logger()


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get(self, id: int) -> User:
        user = await self.repository.get_by_id(id=id)

        if user is None:
            raise ResourceNotFound("User not found")

        return user

    async def create(self, user: UserCreate) -> User:
        log.info(
            "Creating user",
            user_id=user.id,
            first_name=user.first_name,
            username=user.username,
        )

        return await self.repository.create(
            User(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                is_premium=user.is_premium,
                api_key=generate_api_key(),
            )
        )

    async def get_by_api_key(self, api_key: str) -> User:
        user = await self.repository.get_one_or_none(
            self.repository.get_base_stmt().where(User.api_key == api_key)
        )

        if user is None:
            raise ResourceNotFound("User by API key is not found")

        return user

    async def update_balance(self, user: User, new_balance: float) -> User:
        log.info(
            "Updating user balance", prev_balance=user.balance, new_balance=new_balance
        )
        return await self.repository.update(user, {"balance": new_balance})
