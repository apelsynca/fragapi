from src.kit.repository.main import BaseRepository
from src.models import TelegramLogsSource, User


class TelegramLogsSourceRepository(BaseRepository[TelegramLogsSource]):
    model = TelegramLogsSource

    async def get_by_chat_id(
        self, chat_id: str, *, user: User | None = None
    ) -> TelegramLogsSource | None:
        stmt = self.get_base_stmt().where(TelegramLogsSource.chat_id == chat_id)

        if user is not None:
            stmt = stmt.where(TelegramLogsSource.user == user)

        return await self.get_one_or_none(stmt=stmt)
