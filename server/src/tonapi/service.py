import re

from pytonapi.exceptions import TONAPIBadRequestError, TONAPINotFoundError
from pytonapi.rest.models import Transaction as TonAPITransaction
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import Address

from src.config import settings
from src.consts import BADLY_HARD_CODED_LAST_LT, TON_COMMENT_PATTERN
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.logging import get_logger
from src.payment.service import payment as payment_service
from src.tonapi.rest import rest_client
from src.tonapi.schemas import TonAPIWebhookMessage
from src.transaction.service import transaction as transaction_service

log = get_logger()


class TonAPIService:
    ACCOUNT_RAW_ADDRESSES = [
        Address(settings.TON_ADDRESS).to_str(is_user_friendly=False)
    ]

    async def process_webhook_acc_tx(
        self, session: AsyncSession, webhook_message: TonAPIWebhookMessage
    ) -> None:
        if webhook_message.lt < BADLY_HARD_CODED_LAST_LT:
            log.info("Skipping by lt", lt=webhook_message.lt)
            return

        if webhook_message.event_type != "account_tx":
            raise FragError("Wrong event type")

        if webhook_message.account_id not in self.ACCOUNT_RAW_ADDRESSES:
            raise FragError("Wrong account id")

        try:
            # NOTE: here check maybe?
            tonapi_transaction = await self.get_blockchain_transaction(
                tx_hash=webhook_message.tx_hash
            )
        except ResourceNotFound:
            log.warn(
                "tonapi.process_webhook_acc_tx transaction is not found",
                tx_hash=webhook_message.tx_hash,
            )
            return
        except BadRequest:
            log.warn(
                "tonapi.process_webhook_acc_tx transaction bad request",
                tx_hash=webhook_message.tx_hash,
            )
            return
        except Exception as exc:
            log.error(
                "tonapi.process_webhook_acc_tx unknown exception", str_exc=str(exc)
            )
            return

        transaction = await transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )

        hash = self.resolve_payment_hash(tonapi_transaction)
        if hash is None:
            log.warn("Transaction without hash", hash=hash, account_id="0")
            return

        log.info(
            "New valid tonapi transaction", hash=hash, tx_hash=webhook_message.tx_hash
        )

        await payment_service.complete_ton(
            session=session, transaction=transaction, hash=hash
        )

    def resolve_payment_hash(self, tonapi_transaction: TonAPITransaction) -> str | None:
        if tonapi_transaction.in_msg is None:
            return None

        # here test the message type

        if (
            tonapi_transaction.in_msg.decoded_body is None
            or tonapi_transaction.in_msg.decoded_op_name != "text_comment"
        ):
            return None

        text: str = tonapi_transaction.in_msg.decoded_body["text"]
        match = re.match(pattern=TON_COMMENT_PATTERN, string=text)

        if match is not None:
            return match.group(1)

    async def get_blockchain_transaction(self, tx_hash: str) -> TonAPITransaction:
        async with rest_client as client:
            try:
                transaction = await client.blockchain.get_transaction(
                    transaction_id=tx_hash
                )
                return transaction
            except TONAPIBadRequestError:
                raise BadRequest("Transaction with that hash is not found")
            except TONAPINotFoundError:
                raise ResourceNotFound("Transaction with that hash is not found")


tonapi = TonAPIService()
