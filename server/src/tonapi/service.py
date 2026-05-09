import re

from pytonapi.exceptions import TONAPIBadRequestError
from pytonapi.rest import TonapiRestClient
from pytonapi.rest.models import Transaction
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.logging import get_logger
from src.payments.service import payment as payment_service
from src.tonapi.schemas import TonAPIWebhookMessage

log = get_logger()


class TonAPIService:
    def __init__(self) -> None:
        self.rest_client = TonapiRestClient(api_key=settings.TONAPI_API_KEY)

    async def process_webhook_account_tx_message(
        self, session: AsyncSession, message: TonAPIWebhookMessage
    ) -> None:
        if message.event_type != "account_tx":
            raise FragError("Need only account_tx messages")

        transaction = await self.get_blockchain_transaction(tx_hash=message.tx_hash)

        if transaction.in_msg is None:
            log.warn("No transaction out_msgs")
            return

        in_msg = transaction.in_msg

        assert in_msg.decoded_op_name == "text_comment"
        assert in_msg.decoded_body
        comment_text = in_msg.decoded_body["text"]

        payment_hash = self.get_hash_from_comment_text(comment_text)

        if payment_hash is None:
            log.warn(
                "Transaction in the wallet with wrong comment",
                comment_text=comment_text,
            )
            return

        try:
            await payment_service.process_ton_payment(
                session=session, hash=payment_hash
            )
        except ResourceNotFound:
            log.warn(
                "Transaction in the wallet with right comment, but not found",
                comment_text=comment_text,
            )

    async def get_blockchain_transaction(self, tx_hash: str) -> Transaction:
        async with self.rest_client as client:
            try:
                transaction = await client.blockchain.get_transaction(
                    transaction_id=tx_hash
                )
                return transaction
            except TONAPIBadRequestError:
                raise BadRequest("Transaction with that hash is not found")

    def get_hash_from_comment_text(self, comment_text: str) -> str | None:
        # CAREFULL
        match = re.match(pattern=r"[\w\-\ ]+\n\nRef#(.+)", string=comment_text)
        if match is not None:
            return match.group(1)


tonapi = TonAPIService()
