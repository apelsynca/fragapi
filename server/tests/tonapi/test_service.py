from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import Address

from src.config import settings
from src.exceptions import FragError
from src.models import Transaction
from src.payment.service import PaymentService
from src.tonapi.schemas import TonAPIWebhookMessage
from src.tonapi.service import tonapi as tonapi_service
from src.transaction.service import TransactionService
from tests.fixtures.random_objects import create_tonapi_transaction_mock


def get_valid_account_id() -> str:
    return Address(settings.TON_ADDRESS).to_str(is_user_friendly=False)


@pytest.fixture(autouse=True)
def transaction_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.tonapi.service.transaction_service", spec=TransactionService
    )


@pytest.fixture(autouse=True)
def payment_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.tonapi.service.payment_service", spec=PaymentService)


@pytest.fixture
def tonapi_transaction_mock():
    return create_tonapi_transaction_mock()


@pytest.fixture(autouse=True)
def tonapi_rest_client_mock(
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
        account_id=get_valid_account_id(),
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
        account_id=get_valid_account_id(),
        lt=0,
        tx_hash="xxxxxxe0b494f5a8f7c94f8ab37816e98be1a4a95b97c8daeba262e04975cb6c",
    )

    with pytest.raises(FragError):
        await tonapi_service.process_webhook_acc_tx(
            session=session, webhook_message=webhook_message
        )

    get_bc_transa.assert_called_once_with(tx_hash=webhook_message.tx_hash)


def tonapi_right_valid_good_transaction(hash: str) -> MagicMock:
    t = create_tonapi_transaction_mock()

    t.in_msg.decoded_op_name = "text_comment"
    t.in_msg.decoded_body = {"text": tonapi_service.COMMENT_TEMPLATE.format(hash)}

    return t


@pytest.mark.asyncio
async def test_process_valid_makes_right_calls(
    session: AsyncSession,
    transaction_service: MagicMock,
    payment_service: MagicMock,
    tonapi_rest_client_mock: MagicMock,
) -> None:
    tonapi_transaction_mock = tonapi_right_valid_good_transaction(hash="theGoodHash")

    webhook_message = TonAPIWebhookMessage(
        event_type="account_tx",
        account_id=get_valid_account_id(),
        lt=0,
        tx_hash=tonapi_transaction_mock.hash,
    )
    tonapi_rest_client_mock.blockchain.get_transaction.return_value = (
        tonapi_transaction_mock
    )

    # fake transaction based on this data
    transaction = Transaction(
        nano_amount=0,
        hash=tonapi_transaction_mock.hash,
        from_wallet="...",  # TODO: here
        to_wallet="...",  # TODO: here
    )
    transaction_service.create_as_tonapi_internal.return_value = transaction

    await tonapi_service.process_webhook_acc_tx(
        session=session, webhook_message=webhook_message
    )

    transaction_service.create_as_tonapi_internal.assert_called_once_with(
        session=session, tonapi_transaction=tonapi_transaction_mock
    )
    payment_service.complete_ton.assert_called_once_with(
        session=session, transaction=transaction, hash="theGoodHash"
    )
