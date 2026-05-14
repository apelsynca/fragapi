from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture
from pytonapi.exceptions import TONAPIBadRequestError
from pytonapi.rest import TonapiRestClient
from pytonapi.rest.models import Message, Transaction
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import BadRequest, FragError
from src.payments.service import PaymentService
from src.tonapi.schemas import TonAPIWebhookMessage
from src.tonapi.service import tonapi as tonapi_service
from tests.fixtures.random_objects import rstr


def tonapi_transactions_mock(tx_hash: str, ref_hash: str) -> MagicMock:
    transa_mock = MagicMock(spec=Transaction)
    transa_mock.hash = tx_hash
    transa_mock.lt = 0
    transa_mock.success = True
    trans_message_mock = MagicMock(spec=Message)
    trans_message_mock.decoded_op_name = "text_comment"
    trans_message_mock.decoded_body = {"text": f"FragAPI Top-up\n\nRef#{ref_hash}"}
    transa_mock.in_msg = trans_message_mock

    return transa_mock


@pytest.fixture(autouse=True)
def payment_service(mocker: MockerFixture):
    return mocker.patch("src.tonapi.service.payment_service", spec=PaymentService)


@pytest.fixture(autouse=True)
def rest_client(mocker: MockerFixture) -> MagicMock:
    mock_get_trans = AsyncMock(return_value={"status": "ok"})
    mock_blockchain = MagicMock()
    mock_blockchain.get_transaction = mock_get_trans

    mock_rest_client = MagicMock(spec=TonapiRestClient)
    mock_rest_client.__aenter__ = mocker.AsyncMock(return_value=mock_rest_client)
    mock_rest_client.__aexit__ = mocker.AsyncMock(return_value=None)
    mock_rest_client.blockchain = mock_blockchain

    return mocker.patch("src.tonapi.service.tonapi.rest_client", mock_rest_client)


@pytest.mark.asyncio
async def test_calls_to_get_transaction(rest_client: MagicMock) -> None:
    tx_hash = rstr("somehash")
    await tonapi_service.get_blockchain_transaction(tx_hash=tx_hash)

    rest_client.blockchain.get_transaction.assert_called_once_with(
        transaction_id=tx_hash
    )


@pytest.mark.asyncio
async def test_fails_if_event_type_is_wrong(session: AsyncSession) -> None:
    with pytest.raises(FragError):
        await tonapi_service.process_webhook_account_tx_message(
            session=session,
            message=TonAPIWebhookMessage(
                event_type=rstr("something"), account_id="", lt=0, tx_hash=""
            ),
        )


@pytest.mark.asyncio
async def test_raises_bad_request_if_fails_to_find_by_tx_hash(
    rest_client: MagicMock, session: AsyncSession
) -> None:
    rest_client.blockchain.get_transaction.side_effect = TONAPIBadRequestError(
        status=400, message="idk"
    )

    with pytest.raises(BadRequest):
        await tonapi_service.process_webhook_account_tx_message(
            session=session,
            message=TonAPIWebhookMessage(
                event_type="account_tx",
                account_id="0:xxxxxxx",
                lt=0,
                tx_hash="somediffhash",
            ),
        )


# WHAT TO DO IF FOUND TX_HASH IS DIFFERENT?? (probably ignore)


@pytest.mark.asyncio
async def test_calls_process_ton_payment(
    payment_service: MagicMock, rest_client: MagicMock, session: AsyncSession
) -> None:
    message = TonAPIWebhookMessage(
        event_type="account_tx", account_id="any", lt=0, tx_hash="my_tx_hash"
    )
    rest_client.blockchain.get_transaction.return_value = tonapi_transactions_mock(
        tx_hash="my_tx_hash", ref_hash="ThisIsTherefhash"
    )

    await tonapi_service.process_webhook_account_tx_message(
        session=session, message=message
    )

    payment_service.process_ton_payment.assert_called_once_with(
        session=session, hash="ThisIsTherefhash"
    )


# @pytest.mark.asyncio
# async def test_process_same_transaction_twice_raises(
#     session: AsyncSession, rest_client: MagicMock, payment_service: MagicMock
# ) -> None:
#     message = TonAPIWebhookMessage(
#         event_type="account_tx", account_id="any", lt=0, tx_hash="somehardtxhash"
#     )
#     rest_client.blockchain.get_transaction.return_value = tonapi_transactions_mock(
#         tx_hash="my_tx_hash", ref_hash="ThisIsTherefhash"
#     )
#
#     await tonapi_service.process_webhook_account_tx_message(
#         session=session, message=message
#     )
#
#     with pytest.raises(FragError):
#         await tonapi_service.process_webhook_account_tx_message(
#             session=session, message=message
#         )
#
#
# @pytest.mark.asyncio
# async def test_process_webhook_to_the_wrong_wallet_raises(
#     session: AsyncSession, rest_client: MagicMock
# ) -> None:
#     message = TonAPIWebhookMessage(
#         event_type="account_tx", account_id="somewrongone", lt=0, tx_hash="my_tx_hash"
#     )
#     rest_client.blockchain.get_transaction.return_value = tonapi_transactions_mock(
#         tx_hash="my_tx_hash", ref_hash="ThisIsTherefhash"
#     )
#
#     with pytest.raises(FragError):
#         await tonapi_service.process_webhook_account_tx_message(
#             session=session, message=message
#         )
#
#
# @pytest.mark.asyncio
# async def test_saves_wallet_address_in_payment(
#     session: AsyncSession, rest_client: MagicMock
# ) -> None:
#     pass
#
#
# @pytest.mark.asyncio
# async def test_abc_raises(
#     payment_service: MagicMock, rest_client: MagicMock, session: AsyncSession
# ) -> None:
#     message = TonAPIWebhookMessage(
#         event_type="account_tx", account_id="any", lt=0, tx_hash="sometxhash"
#     )
#     transa_mock = MagicMock(spec=Transaction)
#     transa_mock.hash = "differenttxhash"
#     transa_mock.lt = 0
#     transa_mock.success = True
#     trans_message_mock = MagicMock(spec=Message)
#     trans_message_mock.decoded_op_name = "text_comment"
#     trans_message_mock.decoded_body = {"text": "FragAPI Top-up\n\nRef#ThisIsTherefhash"}
#     transa_mock.in_msg = trans_message_mock
#     rest_client.blockchain.get_transaction.return_value = transa_mock
#
#     with pytest.raises(Exception):
#         await tonapi_service.process_webhook_account_tx_message(
#             session=session, message=message
#         )
