import base64

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import begin_cell, to_nano

from src.config import settings
from src.exceptions import BadRequest, ResourceNotFound
from src.kit.ton_connect import TonConnectMessage
from src.models import User
from src.payments.service import payment as payment_service
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_payment


@pytest.mark.asyncio
async def test_processes_ton_payment(
    save_fixture: SaveFixture, user: User, session: AsyncSession
) -> None:
    assert user.balance == 0
    await create_payment(save_fixture, user=user, amount=6.2645, hash="myhash")

    await payment_service.process_ton_payment(session=session, hash="myhash")
    assert user.balance == 6.2645


@pytest.mark.asyncio
async def test_processes_ton_payment_raises_if_not_found(
    save_fixture: SaveFixture, user: User, session: AsyncSession
) -> None:
    assert user.balance == 0
    await create_payment(save_fixture, user=user, amount=6.2645, hash="different_hash")

    with pytest.raises(ResourceNotFound):
        await payment_service.process_ton_payment(session=session, hash="myhash")

    assert user.balance == 0


@pytest.mark.asyncio
async def test_payment_request_right_amount_and_payload(
    session: AsyncSession, user: User, mocker: MockerFixture
) -> None:
    assert 7.252 >= settings.MIN_DEPOSIT_AMOUNT

    spy = mocker.spy(payment_service, "create")

    data = await payment_service.ton_payment_request(
        session=session, user=user, amount=7.252
    )
    spy.assert_called_once_with(session=session, user=user, amount=7.252)

    payment_hash = spy.spy_return.hash
    payload_cell = (
        begin_cell()
        .store_uint(0, 32)
        .store_snake_string(payment_service.COMMENT_TEMPLATE.format(payment_hash))
        .end_cell()
    )
    expected_payload = base64.b64encode(payload_cell.to_boc()).decode("utf-8")

    assert data == TonConnectMessage(
        address=settings.TON_ADDRESS,
        amount=to_nano(7.252),
        payload=expected_payload,
    )


@pytest.mark.asyncio
async def test_payment_raises_min_payment_amount(
    session: AsyncSession, user: User
) -> None:
    with pytest.raises(BadRequest):
        await payment_service.ton_payment_request(
            session=session, user=user, amount=settings.MIN_DEPOSIT_AMOUNT - 0.01
        )
