from pytonapi.exceptions import TONAPIBadRequestError
from pytonapi.rest import TonapiRestClient
from pytonapi.rest.models import Transaction as TonAPITransaction
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import Address

from src.config import settings
from src.exceptions import FragError
from src.payment.service import payment as payment_service
from src.tonapi.schemas import TonAPIWebhookMessage
from src.transaction.service import transaction as transaction_service


class TonAPIService:
    COMMENT_TEMPLATE = "FragAPI top-up\n\nRef#{}"

    def __init__(self) -> None:
        self.rest_client = TonapiRestClient(api_key=settings.TONAPI_API_KEY)

    async def process_webhook_acc_tx(
        self, session: AsyncSession, webhook_message: TonAPIWebhookMessage
    ) -> None:
        if webhook_message.event_type != "account_tx":
            raise FragError("Wrong event type")

        # for now)
        account_ids = [Address(settings.TON_ADDRESS).to_str(is_user_friendly=False)]

        # TODO: test that this should raise after creating the blockchain transaction
        if webhook_message.account_id not in account_ids:
            raise FragError("Wrong account id")

        tonapi_transaction = await self.get_blockchain_transaction(
            tx_hash=webhook_message.tx_hash
        )

        transaction = await transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )

        # resolve hash here
        hash = self.resolve_payment_hash(tonapi_transaction)

        # log.info  here

        await payment_service.complete_ton(
            session=session, transaction=transaction, hash=hash
        )

        # send notification task here

    def resolve_payment_hash(self, tonapi_transaction: TonAPITransaction) -> str | None:
        if tonapi_transaction.in_msg is None:
            return None
        if (
            tonapi_transaction.in_msg.decoded_body is None
            or tonapi_transaction.in_msg.decoded_op_name != "text-msg..."
        ):
            return None

        return tonapi_transaction.in_msg.decoded_body["text"]

    async def get_blockchain_transaction(self, tx_hash: str) -> TonAPITransaction:
        async with self.rest_client as client:
            try:
                transaction = await client.blockchain.get_transaction(
                    transaction_id=tx_hash
                )
                return transaction
            except TONAPIBadRequestError:
                raise FragError("Transaction with that hash is not found")


tonapi = TonAPIService()
