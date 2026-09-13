from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import BadRequest, ResourceNotFound
from src.models import TelegramLogsSource, User
from src.telegram_log.repository import TelegramLogsSourceRepository


def validate_chat_id_or_smth(chat_id: int | str) -> str:
    # later can do a better validation or smth
    return str(chat_id)


class TelegramLogService:
    async def get_all_sources(
        self, session: AsyncSession, user: User
    ) -> Sequence[TelegramLogsSource]:
        repository = TelegramLogsSourceRepository.from_session(session)

        stmt = repository.get_base_stmt().where(TelegramLogsSource.user == user)
        return await repository.get_all(stmt)

    async def create_source(
        self, session: AsyncSession, user: User, chat_id: int | str
    ) -> TelegramLogsSource:
        """
        NOTE: not used yet. meant to be used when 1+ sources allowed.
        """

        chat_id = validate_chat_id_or_smth(chat_id)
        repository = TelegramLogsSourceRepository.from_session(session)

        stmt = select(TelegramLogsSource).where(TelegramLogsSource.user == user)
        existing_sources = await repository.get_all(stmt=stmt)

        if len(existing_sources) > 0:
            raise BadRequest("Aready have a source")

        return await repository.create(
            TelegramLogsSource(chat_id=chat_id, user=user), flush=True
        )

    async def get_source_by_chat_id(
        self, session: AsyncSession, chat_id: int | str
    ) -> TelegramLogsSource:
        chat_id = validate_chat_id_or_smth(chat_id)
        repository = TelegramLogsSourceRepository.from_session(session)

        source = await repository.get_by_chat_id(chat_id=chat_id)

        if source is None:
            raise ResourceNotFound("Source is not found by chat_id")

        return source

    async def set_source(
        self, session: AsyncSession, user: User, chat_id: int | str
    ) -> TelegramLogsSource:
        chat_id = validate_chat_id_or_smth(chat_id)
        repository = TelegramLogsSourceRepository.from_session(session)

        await session.execute(
            delete(TelegramLogsSource).where(TelegramLogsSource.user == user)
        )

        return await repository.create(
            TelegramLogsSource(chat_id=chat_id, user=user), flush=True
        )

    async def delete(self, session: AsyncSession, source: TelegramLogsSource) -> None:
        repository = TelegramLogsSourceRepository.from_session(session)
        await repository.delete(source)


telegram_log = TelegramLogService()
