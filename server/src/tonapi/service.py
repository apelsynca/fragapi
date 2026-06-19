import asyncio

import structlog
from pytonapi.exceptions import TONAPIBadRequestError, TONAPINotFoundError
from pytonapi.rest import TonapiRestClient
from pytonapi.rest.models import Transaction as TonAPITransaction
from ton_core import Address

from src.config import settings
from src.deposit.service import deposit as deposit_service
from src.deposit.ton_payload import TonDepositPayload
from src.exceptions import BadRequest, FragError, ResourceNotFound
from src.logging import Logger
from src.postgres import AsyncSession
from src.ton_transaction.service import ton_transaction as ton_transaction_service
from src.tonapi.rest import rest_client
from src.tonapi.schemas import TonAPIWebhookMessage

log: Logger = structlog.get_logger()


class TonAPIService:
    ACCOUNT_RAW_ADDRESSES = [
        Address(settings.TON_ADDRESS).to_str(is_user_friendly=False)
    ]

    RETRY_LIMIT: int = 3
    SEARCH_RETRY_SLEEP_FOR: float = 2.5

    _last_lt: int = 0

    def __init__(self) -> None:
        # PERF: starting value prefetch?! (rethink if multi-wallet)
        self._last_lt = 82005139000003

    async def process_webhook_acc_tx(
        self, session: AsyncSession, webhook_message: TonAPIWebhookMessage
    ) -> None:
        if webhook_message.lt < self._last_lt:
            log.warning(
                "tonapi.process_webhook_acc_tx skipping by lt", lt=webhook_message.lt
            )
            return

        if webhook_message.event_type != "account_tx":
            raise FragError("Wrong event type")

        if webhook_message.account_id not in self.ACCOUNT_RAW_ADDRESSES:
            raise FragError("Wrong account id")

        try:
            await asyncio.sleep(0.85)  # let tonapi process it
            tonapi_transaction = await self.get_blockchain_transaction(
                tx_hash=webhook_message.tx_hash
            )
        except ResourceNotFound:
            log.warning(
                "tonapi.process_webhook_acc_tx transaction is not found",
                tx_hash=webhook_message.tx_hash,
            )
            return
        except BadRequest:
            log.warning(
                "tonapi.process_webhook_acc_tx transaction bad request",
                tx_hash=webhook_message.tx_hash,
            )
            return
        except Exception as exc:
            log.error(
                "tonapi.process_webhook_acc_tx unknown exception", str_exc=str(exc)
            )
            return

        transaction = await ton_transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )

        try:
            ton_dep_payload = TonDepositPayload.from_tonapi_transaction(
                tonapi_transaction
            )
        except ValueError:
            log.warning(
                "tonapi.process_webhook_acc_tx transaction with unresolved payload hash",
                account_id=webhook_message.account_id,
            )
            return

        log.info(
            "tonapi.process_webhook_acc_tx new valid transaction",
            hash=ton_dep_payload.ref_hash,
            tx_hash=webhook_message.tx_hash,
            account_id=webhook_message.account_id,
        )

        if webhook_message.lt > self._last_lt:
            self._last_lt = webhook_message.lt

        await deposit_service.complete_ton(
            session=session,
            transaction=transaction,
            ref_hash=ton_dep_payload.ref_hash,
        )

    async def get_blockchain_transaction(self, tx_hash: str) -> TonAPITransaction:
        async with rest_client as client:
            return await self._search_bc_trans_with_retry(
                client=client, tx_hash=tx_hash
            )

    async def _search_bc_trans_with_retry(
        self, client: TonapiRestClient, tx_hash: str, *, retry_num: int = 0
    ) -> TonAPITransaction:
        if retry_num >= self.RETRY_LIMIT:
            raise ValueError("Retry limit exceeded")

        try:
            return await client.blockchain.get_transaction(transaction_id=tx_hash)
        except TONAPIBadRequestError:
            raise BadRequest("Transaction with that hash is not found")
        except TONAPINotFoundError:
            if retry_num + 1 < self.RETRY_LIMIT:
                await asyncio.sleep(self.SEARCH_RETRY_SLEEP_FOR)
                return await self._search_bc_trans_with_retry(
                    client=client, tx_hash=tx_hash, retry_num=retry_num + 1
                )
            raise ResourceNotFound("Transaction with that hash is not found")


tonapi = TonAPIService()
