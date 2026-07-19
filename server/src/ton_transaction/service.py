from pytonapi.rest.models import Transaction as TonAPITransaction
from ton_core import Address, ExternalMessage

from src.exceptions import FragRequestValidationError
from src.kit.ton_connect import TonConnectTransaction
from src.models import TonTransaction
from src.postgres import AsyncSession
from src.ton_transaction.repository import TonTransactionRepository


class TonTransactionService:
    """Dont confuze with TransactionService (prev. FragmentTransactionService)"""

    async def create_as_tc(
        self, session: AsyncSession, tc_transaction: TonConnectTransaction
    ) -> TonTransaction:
        tc_msg = tc_transaction.messages[0]
        ext_msg = ExternalMessage(
            dest=Address(tc_msg.address), body=tc_msg.get_payload_cell()
        )

        repository = TonTransactionRepository.from_session(session)
        return await repository.create(
            TonTransaction(
                nano_amount=tc_msg.amount,
                hash=None,
                message_hash=ext_msg.normalized_hash,
                from_address=tc_transaction.from_address,
                to_address=Address(tc_msg.address).to_str(is_user_friendly=False),
            ),
            flush=True,
        )

    async def create_as_tonapi_internal(
        self, session: AsyncSession, tonapi_transaction: TonAPITransaction
    ) -> TonTransaction:
        if not tonapi_transaction.success:
            raise FragRequestValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ("body", "success"),
                        "msg": "TonAPI internal transaction must be successfull",
                        "input": tonapi_transaction.success,
                    }
                ]
            )

        if tonapi_transaction.in_msg is None:
            raise FragRequestValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ("body", "in_msg"),
                        "msg": "TonAPI internal transaction must have the internal message",
                        "input": tonapi_transaction.in_msg,
                    }
                ]
            )

        in_msg = tonapi_transaction.in_msg
        if in_msg.msg_type != "int_msg":
            raise FragRequestValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ("body", "in_msg", "msg_type"),
                        "msg": "TonAPI internal transaction in_msg type must be internal",
                        "input": in_msg.msg_type,
                    }
                ]
            )

        if len(tonapi_transaction.out_msgs) != 0:
            raise FragRequestValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ("body", "out_msgs"),
                        "msg": "TonAPI internal transaction must have zero out msgs",
                        "input": tonapi_transaction.out_msgs,
                    }
                ]
            )

        if in_msg.destination is None:
            raise FragRequestValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ("body", "in_msg", "destination"),
                        "msg": "TonAPI internal transaction in_msg must have a destination",
                        "input": in_msg.destination,
                    }
                ]
            )
        if in_msg.source is None:
            raise FragRequestValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ("body", "in_msg", "source"),
                        "msg": "TonAPI internal transaction in_msg must have a source",
                        "input": in_msg.source,
                    }
                ]
            )

        repository = TonTransactionRepository.from_session(session)

        return await repository.create(
            TonTransaction(
                hash=tonapi_transaction.hash,
                nano_amount=in_msg.value,
                from_address=in_msg.source.address,
                to_address=in_msg.destination.address,
            ),
            flush=True,
        )


ton_transaction = TonTransactionService()
