import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import BadRequest
from src.models import TelegramLogsSource, User
from src.telegram_log.service import telegram_log as telegram_log_service

# PERF: test cannot create with the same user and chat_id if later more than one (perf only when more than one will be disabled)


@pytest.mark.asyncio
async def test_create_creates(session: AsyncSession, user: User) -> None:
    tg_logs_source = await telegram_log_service.create_source(
        session=session, user=user, chat_id=9919
    )

    assert tg_logs_source.user == user
    assert tg_logs_source.chat_id == "9919"

    # test created really
    second_tg_logs_source = await session.get_one(TelegramLogsSource, tg_logs_source.id)
    assert second_tg_logs_source.user == user
    assert second_tg_logs_source.chat_id == "9919"


@pytest.mark.asyncio
async def test_create_cannot_create_more_than_one(
    session: AsyncSession, user: User
) -> None:
    tg_logs_source = await telegram_log_service.create_source(
        session=session, user=user, chat_id=9998189
    )

    assert tg_logs_source.user == user
    assert tg_logs_source.chat_id == "9998189"

    with pytest.raises(BadRequest):
        await telegram_log_service.create_source(
            session=session, user=user, chat_id="someotherone"
        )


@pytest.mark.asyncio
async def test_set_source_chat_id_if_empty_before_but_other_sources(
    session: AsyncSession, user: User, user_second: User
) -> None:
    await telegram_log_service.create_source(
        session=session, user=user_second, chat_id="anyChatId"
    )

    # just for safety lol
    stmt = select(TelegramLogsSource).where(TelegramLogsSource.user == user)
    telegram_logs_sources = (await session.scalars(stmt)).unique().all()
    assert len(telegram_logs_sources) == 0

    source = await telegram_log_service.set_source(
        session=session, user=user, chat_id="someKindOfChatId"
    )

    assert source.chat_id == "someKindOfChatId"
    assert source.user == user

    stmt = select(TelegramLogsSource).where(TelegramLogsSource.user == user)
    telegram_logs_sources = (await session.scalars(stmt)).unique().all()
    assert len(telegram_logs_sources) == 1
    assert telegram_logs_sources[0].chat_id == "someKindOfChatId"
    assert telegram_logs_sources[0].user_id == user.id

    stmt = select(TelegramLogsSource)
    telegram_logs_sources = (await session.scalars(stmt)).unique().all()
    assert len(telegram_logs_sources) == 2


@pytest.mark.asyncio
async def test_set_source_chat_id_if_non_empty_before(
    session: AsyncSession, user: User
) -> None:
    await telegram_log_service.create_source(
        session=session, user=user, chat_id="someKindOfChatId"
    )

    # 1 - then
    stmt = select(TelegramLogsSource).where(TelegramLogsSource.user == user)
    telegram_logs_sources = (await session.scalars(stmt)).unique().all()
    assert len(telegram_logs_sources) == 1

    new_source = await telegram_log_service.set_source(
        session=session, user=user, chat_id="diffieChatId"
    )

    assert new_source.chat_id == "diffieChatId"
    assert new_source.user == user

    # 2 - then (make sure you can create only one source for now, later can do more)
    stmt = select(TelegramLogsSource).where(TelegramLogsSource.user == user)
    telegram_logs_sources = (await session.scalars(stmt)).unique().all()
    assert len(telegram_logs_sources) == 1

    assert telegram_logs_sources[0].chat_id == "diffieChatId"
    assert telegram_logs_sources[0].user_id == user.id
