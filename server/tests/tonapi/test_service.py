from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import FragError
from src.payment.service import PaymentService
from src.tonapi.schemas import TonAPIWebhookMessage
from src.tonapi.service import tonapi as tonapi_service
from src.transaction.service import TransactionService
from tests.fixtures.random_objects import create_tonapi_transaction_mock


@pytest.fixture(autouse=True)
def transaction_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.tonapi.service.transaction_service", spec=TransactionService
    )


@pytest.fixture(autouse=True)
def payment_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.tonapi.service.payment_service", spec=PaymentService)


@pytest.fixture
def tonapi_transaction_mock() -> MagicMock:
    return create_tonapi_transaction_mock(hash="righthash")


@pytest.fixture(autouse=True)
def fake_tonapi_rest(
    mocker: MockerFixture, tonapi_transaction_mock: MagicMock
) -> MagicMock:
    mock_inner_client = mocker.MagicMock()
    mock_inner_client.blockchain.get_transaction = mocker.AsyncMock(
        return_value=tonapi_transaction_mock
    )

    mock_rest_client = mocker.MagicMock()
    mock_rest_client.__aenter__ = mocker.AsyncMock(return_value=mock_inner_client)
    mock_rest_client.__aexit__ = mocker.AsyncMock(return_value=None)

    mocker.patch.object(tonapi_service, "rest_client", new=mock_rest_client)

    return mock_inner_client


@pytest.mark.asyncio
async def test_raises_if_wrong_event_type(session: AsyncSession) -> None:
    webhook_message = TonAPIWebhookMessage(
        event_type="some_other_event",
        account_id=tonapi_service.ACCOUNT_RAW_ADDRESSES[0],
        lt=0,
        tx_hash="da8befe0b494f5a8f7c94f8ab37816e98be1a4a95b97c8daeba262e04975cb6c",
    )

    with pytest.raises(FragError):
        await tonapi_service.process_webhook_acc_tx(
            session=session, webhook_message=webhook_message
        )


@pytest.mark.asyncio
async def test_process_webhook_acc_tx_raises_if_wrong_account_id(
    session: AsyncSession,
) -> None:
    webhook_message = TonAPIWebhookMessage(
        event_type="account_tx",
        account_id="0:11111ad51e1cc3626cc4c589088bdcc68ea57f9e6d33c51447c6bf7a200ebc9f",
        lt=0,
        tx_hash="da8befe0b494f5a8f7c94f8ab37816e98be1a4a95b97c8daeba262e04975cb6c",
    )

    with pytest.raises(FragError):
        await tonapi_service.process_webhook_acc_tx(
            session=session, webhook_message=webhook_message
        )


@pytest.mark.asyncio
async def test_process_webhook_acc_tx_raises_if_transaction_not_found_by_hash(
    session: AsyncSession, mocker: MockerFixture
) -> None:
    get_bc_transa = mocker.patch.object(
        tonapi_service, "get_blockchain_transaction", side_effect=FragError("Errr")
    )

    webhook_message = TonAPIWebhookMessage(
        event_type="account_tx",
        account_id=tonapi_service.ACCOUNT_RAW_ADDRESSES[0],
        lt=0,
        tx_hash="xxxxxxe0b494f5a8f7c94f8ab37816e98be1a4a95b97c8daeba262e04975cb6c",
    )

    with pytest.raises(FragError):
        await tonapi_service.process_webhook_acc_tx(
            session=session, webhook_message=webhook_message
        )

    get_bc_transa.assert_called_once_with(tx_hash=webhook_message.tx_hash)


@pytest.mark.asyncio
async def test_logs_if_no_hash_found(
    session: AsyncSession, mocker: MockerFixture, fake_tonapi_rest: MagicMock
) -> None:
    fake_tonapi_rest.blockchain.get_transaction = mocker.AsyncMock(
        return_value=create_tonapi_transaction_mock(hash="righthash")
    )

    log_mock = mocker.patch("src.tonapi.service.log")

    webhook_message = TonAPIWebhookMessage(
        event_type="account_tx",
        account_id=tonapi_service.ACCOUNT_RAW_ADDRESSES[0],
        lt=0,
        tx_hash="xxxxxxe0b494f5a8f7c94f8ab37816e98be1a4a95b97c8daeba262e04975cb6c",
    )

    await tonapi_service.process_webhook_acc_tx(
        session=session, webhook_message=webhook_message
    )

    log_mock.warn.assert_called_once_with(
        "Transaction without hash",
        hash=None,
        account_id=tonapi_service.ACCOUNT_RAW_ADDRESSES[0],
        tx_hash="xxxxxxe0b494f5a8f7c94f8ab37816e98be1a4a95b97c8daeba262e04975cb6c",
    )


# @pytest.mark.asyncio
# async def test_logs_fails(session: AsyncSession, mocker: MockerFixture) -> None:
#     log_mock = mocker.patch("src.tonapi.service.log")
#
#     await tonapi_service.process_webhook_acc_tx(
#         session=session, webhook_message=webhook_message
#     )
#
#     log_mock.assert_called_once_with()
