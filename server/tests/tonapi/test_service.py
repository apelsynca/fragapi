import random
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture
from pytonapi.exceptions import TONAPIBadRequestError, TONAPINotFoundError
from pytonapi.rest import TonapiRestClient
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import Address

from src.config import settings
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.payment.service import PaymentService
from src.tonapi.schemas import TonAPIWebhookMessage
from src.tonapi.service import tonapi as tonapi_service
from tests.fixtures.random_objects import rstr


@pytest.fixture(autouse=True)
def payment_service(mocker: MockerFixture) -> MagicMock:
    mock = mocker.patch("src.tonapi.service.payment_service", spec=PaymentService)
    mock.ACCOUNT_RAW_ADDRESSES = [
        Address(settings.TON_ADDRESS).to_str(is_user_friendly=False)
    ]

    return mock


@pytest.fixture(autouse=True)
def rest_bc(mocker: MockerFixture) -> MagicMock:
    mock_client = AsyncMock()
    mock_client.blockchain.get_transaction.side_effect = TONAPINotFoundError(
        status=404, message="Not found"
    )  # good

    mock_rest = mocker.patch("src.tonapi.service.rest_client", spec=TonapiRestClient)

    mock_rest.__aenter__.return_value = mock_client
    mock_rest.__aexit__.return_value = None

    return mock_client  # important


@pytest.mark.asyncio
async def test_raises_wrong_event_type(session: AsyncSession) -> None:
    webhook_message = TonAPIWebhookMessage(
        event_type=rstr("wrong_event"),
        account_id=rstr("canbeany"),
        lt=0,
        tx_hash=rstr("canbeany"),
    )

    with pytest.raises(FragError, match="event type"):
        await tonapi_service.process_webhook_acc_tx(
            session=session, webhook_message=webhook_message
        )


@pytest.mark.asyncio
async def test_raises_wrong_account_id(session: AsyncSession) -> None:
    webhook_message = TonAPIWebhookMessage(
        event_type="account_tx",
        account_id=rstr("canbeany"),
        lt=0,
        tx_hash=rstr("canbeany"),
    )

    with pytest.raises(FragError, match="account id"):
        await tonapi_service.process_webhook_acc_tx(
            session=session, webhook_message=webhook_message
        )


@pytest.mark.asyncio
async def test_get_bc_trans_raises_not_found_on_tonapi_not_found(
    rest_bc: MagicMock,
) -> None:
    rest_bc.blockchain.get_transaction.side_effect = TONAPINotFoundError(
        status=404, message="My message"
    )

    with pytest.raises(ResourceNotFound):
        await tonapi_service.get_blockchain_transaction(
            tx_hash="0e7cc4e87ad9be07b952be5c11b23c47ba6df0009773b0898a0eb5a58bffb87c"
        )


@pytest.mark.asyncio
async def test_get_bc_trans_raises_bad_request_on_tonapi_bad_request(
    rest_bc: MagicMock,
) -> None:
    rest_bc.get_transaction.side_effect = TONAPIBadRequestError(
        status=400, message="Bad request"
    )

    with pytest.raises(BadRequest):
        await tonapi_service.get_blockchain_transaction(tx_hash=rstr("invalid-hash"))


@pytest.mark.asyncio
async def test_logs_on_get_tx_bad_request_and_does_not_call(
    payment_service: MagicMock,
    session: AsyncSession,
    mocker: MockerFixture,
    rest_bc: MagicMock,
) -> None:
    log_mock = mocker.patch("src.tonapi.service.log")
    webhook_message = TonAPIWebhookMessage(
        event_type="account_tx",
        account_id=payment_service.ACCOUNT_RAW_ADDRESSES[0],
        lt=random.randint(1, 9999999),
        tx_hash="xxxx",
    )
    rest_bc.blockchain.get_transaction.side_effect = TONAPINotFoundError(
        status=404, message="Bad request"
    )
    # rest_bc.blockchain.get_transaction.side_effect = TONAPIBadRequestError(
    #     status=400, message="Bad request"
    # )

    # When
    await tonapi_service.process_webhook_acc_tx(
        session=session, webhook_message=webhook_message
    )

    payment_service.complete_ton.assert_not_called()
    log_mock.warn.assert_called_once_with(
        "tonapi.process_webhook_acc_tx transaction is not found",
        tx_hash="xxxx",
    )


@pytest.mark.asyncio
async def test_logs_on_get_tx_any_error_and_does_not_call(
    payment_service: MagicMock,
    session: AsyncSession,
    mocker: MockerFixture,
    rest_bc: MagicMock,
) -> None:
    log_mock = mocker.patch("src.tonapi.service.log")
    webhook_message = TonAPIWebhookMessage(
        event_type="account_tx",
        account_id=payment_service.ACCOUNT_RAW_ADDRESSES[0],
        lt=random.randint(1, 9999999),
        tx_hash="xxxx",
    )
    exc = Exception("Random exception")
    rest_bc.blockchain.get_transaction.side_effect = exc

    # When
    await tonapi_service.process_webhook_acc_tx(
        session=session, webhook_message=webhook_message
    )

    payment_service.complete_ton.assert_not_called()
    log_mock.error.assert_called_once_with(
        "tonapi.process_webhook_acc_tx unknown exception", str_exc=str(exc)
    )
