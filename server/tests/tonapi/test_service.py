from secrets import token_urlsafe
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture
from pytonapi.exceptions import TONAPIBadRequestError, TONAPINotFoundError
from pytonapi.rest import TonapiRestClient
from pytonapi.rest.models import Message as TonAPIMessage
from pytonapi.rest.models import Transaction as TonAPITransaction
from ton_core import Address

from src.deposit.service import DepositService
from src.deposit.ton_payload import TonDepositPayload
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.logging import Logger
from src.models import TonTransaction
from src.postgres import AsyncSession
from src.ton_transaction.service import TonTransactionService
from src.tonapi.schemas import TonAPIWebhookMessage
from src.tonapi.service import tonapi as tonapi_service
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_ton_transaction, rstr


@pytest.fixture
def transaction_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.tonapi.service.ton_transaction_service", spec=TonTransactionService
    )


@pytest.fixture
def deposit_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.tonapi.service.deposit_service", spec=DepositService)


@pytest.fixture(autouse=True)
def sleep_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("src.tonapi.service.asyncio.sleep", new_callable=AsyncMock)


@pytest.fixture(autouse=True)
def tonapi_rest_client_mock(mocker: MockerFixture) -> MagicMock:
    mock_client = AsyncMock()
    mock_rest = mocker.patch("src.tonapi.service.rest_client", spec=TonapiRestClient)

    mock_rest.__aenter__.return_value = mock_client
    mock_rest.__aexit__.return_value = None

    return mock_client  # important


@pytest.fixture
def valid_webhook_message() -> TonAPIWebhookMessage:
    return get_webhook_message(
        event_type="account_tx",
        account_id=tonapi_service.ACCOUNT_RAW_ADDRESSES[0],
        tx_hash="97264395BD65A255A429B11326C84128B7D70FFED7949ABAE3036D506BA38621",
    )


def get_webhook_message(
    *,
    event_type: str | None = "account_tx",
    account_id: str | None = None,
    tx_hash: str | None = None,
    lt: int | None = None,
) -> TonAPIWebhookMessage:
    return TonAPIWebhookMessage(
        event_type=rstr("wrong_event") if event_type is None else event_type,
        account_id=rstr("canbeany") if account_id is None else account_id,
        lt=tonapi_service._last_lt + 1000 if lt is None else lt,
        tx_hash=rstr("canbeany") if tx_hash is None else tx_hash,
    )


@pytest.mark.asyncio
async def test_raises_wrong_event_type(session: AsyncSession) -> None:
    webhook_message = get_webhook_message(event_type="wrong_event")

    with pytest.raises(FragError, match="event type"):
        await tonapi_service.process_webhook_acc_tx(
            session=session, webhook_message=webhook_message
        )


@pytest.mark.asyncio
async def test_raises_wrong_account_id(session: AsyncSession) -> None:
    wrong_account_id = Address(
        "UQBKDU9Ws58AyUg32EFMliW2eTNloL6wKXcWnZu-hZMiN-Do"
    ).to_str(is_user_friendly=False)
    assert wrong_account_id not in tonapi_service.ACCOUNT_RAW_ADDRESSES

    webhook_message = get_webhook_message(
        event_type="account_tx", account_id=wrong_account_id
    )

    with pytest.raises(FragError, match="account id"):
        await tonapi_service.process_webhook_acc_tx(
            session=session, webhook_message=webhook_message
        )


@pytest.mark.asyncio
async def test_get_bc_trans_raises_not_found_on_tonapi_not_found(
    tonapi_rest_client_mock: MagicMock,
) -> None:
    tonapi_rest_client_mock.blockchain.get_transaction.side_effect = (
        TONAPINotFoundError(status=404, message="My message")
    )

    with pytest.raises(ResourceNotFound):
        await tonapi_service.get_blockchain_transaction(
            tx_hash="0e7cc4e87ad9be07b952be5c11b23c47ba6df0009773b0898a0eb5a58bffb87c"
        )


@pytest.mark.asyncio
async def test_get_bc_trans_raises_bad_request_on_tonapi_bad_request(
    tonapi_rest_client_mock: MagicMock, mocker: MockerFixture
) -> None:
    tonapi_rest_client_mock.blockchain.get_transaction.side_effect = (
        TONAPIBadRequestError(status=400, message="Bad request")
    )

    get_blockchain_transaction_spy = mocker.spy(
        tonapi_service, "get_blockchain_transaction"
    )

    with pytest.raises(BadRequest):
        await tonapi_service.get_blockchain_transaction(tx_hash=rstr("invalid-hash"))

    get_blockchain_transaction_spy.assert_called_once()


@pytest.mark.asyncio
async def test_get_bc_trans_retries(
    tonapi_rest_client_mock: MagicMock, mocker: MockerFixture
) -> None:
    tonapi_rest_client_mock.blockchain.get_transaction.side_effect = (
        TONAPINotFoundError(status=404, message="Not found")
    )
    procc_bc_trans_with_retry_spy = mocker.spy(
        tonapi_service, "_search_bc_trans_with_retry"
    )

    # Raises, but calls retries
    with pytest.raises(ResourceNotFound):
        await tonapi_service.get_blockchain_transaction(
            tx_hash=rstr("good hash need here")
        )

    assert procc_bc_trans_with_retry_spy.call_count == tonapi_service.RETRY_LIMIT


@pytest.mark.asyncio
async def test_logs_on_get_tx_not_found_and_does_not_call(
    deposit_service: MagicMock,
    session: AsyncSession,
    mocker: MockerFixture,
    tonapi_rest_client_mock: MagicMock,
    valid_webhook_message: TonAPIWebhookMessage,
) -> None:
    log_mock = mocker.patch("src.tonapi.service.log")
    tonapi_rest_client_mock.blockchain.get_transaction.side_effect = (
        TONAPINotFoundError(status=404, message="Not found or smth")
    )

    # When
    await tonapi_service.process_webhook_acc_tx(
        session=session, webhook_message=valid_webhook_message
    )

    deposit_service.complete_ton.assert_not_called()
    log_mock.warning.assert_called_once_with(
        "tonapi.process_webhook_acc_tx transaction is not found",
        tx_hash="97264395BD65A255A429B11326C84128B7D70FFED7949ABAE3036D506BA38621",
    )


@pytest.mark.asyncio
async def test_logs_on_get_tx_bad_request_and_does_not_call(
    deposit_service: MagicMock,
    session: AsyncSession,
    mocker: MockerFixture,
    tonapi_rest_client_mock: MagicMock,
) -> None:
    webhook_message = get_webhook_message(
        tx_hash="bad_tx_hash",
        account_id=tonapi_service.ACCOUNT_RAW_ADDRESSES[0],
    )

    log_mock = mocker.patch("src.tonapi.service.log")
    tonapi_rest_client_mock.blockchain.get_transaction.side_effect = (
        TONAPIBadRequestError(status=400, message="Bad request")
    )

    # When
    await tonapi_service.process_webhook_acc_tx(
        session=session, webhook_message=webhook_message
    )

    deposit_service.complete_ton.assert_not_called()
    log_mock.warning.assert_called_once_with(
        "tonapi.process_webhook_acc_tx transaction bad request",
        tx_hash="bad_tx_hash",
    )


@pytest.mark.asyncio
async def test_logs_on_get_tx_any_error_and_does_not_call(
    deposit_service: MagicMock,
    session: AsyncSession,
    mocker: MockerFixture,
    tonapi_rest_client_mock: MagicMock,
    valid_webhook_message: TonAPIWebhookMessage,
) -> None:
    log_mock = mocker.patch("src.tonapi.service.log")
    exc = Exception("Random exception")
    tonapi_rest_client_mock.blockchain.get_transaction.side_effect = exc

    # When
    await tonapi_service.process_webhook_acc_tx(
        session=session, webhook_message=valid_webhook_message
    )

    deposit_service.complete_ton.assert_not_called()
    log_mock.error.assert_called_once_with(
        "tonapi.process_webhook_acc_tx unknown exception", str_exc=str(exc)
    )


@pytest.mark.asyncio
async def test_all_good_right_calls_and_sets_lt(
    save_fixture: SaveFixture,
    deposit_service: MagicMock,
    session: AsyncSession,
    mocker: MockerFixture,
    tonapi_rest_client_mock: MagicMock,
    transaction_service_mock: MagicMock,
) -> None:
    ref_hash = token_urlsafe(12)  # Random hashik

    webhook_message = get_webhook_message(
        event_type="account_tx",
        account_id=tonapi_service.ACCOUNT_RAW_ADDRESSES[0],
        lt=99999999999999999111,
        tx_hash="my_tx_hash_SHOULD_REDO",
    )

    usual_transaction = await create_ton_transaction(
        save_fixture, amount=0, message_hash=""
    )
    transaction_service_mock.create_as_tonapi_internal.return_value = usual_transaction

    tonapi_tx_mock = MagicMock(spec=TonAPITransaction, autospec=True)
    tonapi_rest_client_mock.blockchain.get_transaction.return_value = tonapi_tx_mock

    mocker.patch.object(
        TonDepositPayload,
        "from_tonapi_transaction",
        return_value=TonDepositPayload(ref_hash),
    )

    # Doing shi
    await tonapi_service.process_webhook_acc_tx(
        session=session, webhook_message=webhook_message
    )

    tonapi_rest_client_mock.blockchain.get_transaction.assert_called_once_with(
        transaction_id="my_tx_hash_SHOULD_REDO"
    )
    transaction_service_mock.create_as_tonapi_internal.assert_called_once_with(
        session=session, tonapi_transaction=tonapi_tx_mock
    )
    deposit_service.complete_ton.assert_called_once_with(
        session=session, transaction=usual_transaction, ref_hash=ref_hash
    )

    assert tonapi_service._last_lt >= 99999999999999999111


@pytest.mark.asyncio
async def test_if_wrong_comment_hash_resolve_logs_and_returns(
    transaction: TonTransaction,
    transaction_service_mock: MagicMock,
    session: AsyncSession,
    valid_webhook_message: TonAPIWebhookMessage,
    mocker: MockerFixture,
    tonapi_rest_client_mock: MagicMock,
) -> None:
    log_mock = mocker.patch("src.tonapi.service.log", spec=Logger)

    tonapi_tx_mock = MagicMock(spec=TonAPITransaction, autospec=True)
    tonapi_tx_mock.success = True
    tonapi_tx_mock.msg_type = "in_msg"
    in_msg = MagicMock(spec=TonAPIMessage)
    in_msg.decoded_body = {"text": "Completily wrong text"}
    in_msg.decoded_op_name = "text_comment"
    tonapi_tx_mock.in_msg = in_msg

    tonapi_rest_client_mock.blockchain.get_transaction.return_value = tonapi_tx_mock

    from_ta_t_mock = mocker.spy(TonDepositPayload, "from_tonapi_transaction")
    transaction_service_mock.create_as_tonapi_internal.return_value = transaction

    await tonapi_service.process_webhook_acc_tx(
        session=session, webhook_message=valid_webhook_message
    )

    from_ta_t_mock.assert_called_once_with(tonapi_tx_mock)
    log_mock.warning.assert_called_once_with(
        "tonapi.process_webhook_acc_tx transaction with unresolved payload hash",
        account_id=valid_webhook_message.account_id,
    )
