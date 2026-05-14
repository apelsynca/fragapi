from pytonapi.rest.models import Transaction as TonAPITransaction
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import FragRequestValidationError
from src.models import Transaction
from src.transaction.repository import TransactionRepository


class TransactionService:
    async def create_as_tc(
        self,
        session: AsyncSession,
        nano_amount: int,
        message_hash: str,
        from_address: str,
        to_address: str,
    ) -> Transaction:
        repository = TransactionRepository.from_session(session)

        transaction = Transaction(
            nano_amount=nano_amount,
            message_hash=message_hash,
            from_address=from_address,
            to_address=to_address,
        )

        return await repository.create(transaction, flush=True)

    async def create_as_tonapi_internal(
        self, session: AsyncSession, tonapi_transaction: TonAPITransaction
    ) -> Transaction:
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

        transaction = Transaction(
            hash=tonapi_transaction.hash,
            nano_amount=in_msg.value,
            from_address=in_msg.source.address,
            to_address=in_msg.destination.address,
        )

        repository = TransactionRepository.from_session(session)

        return await repository.create(transaction, flush=True)


transaction = TransactionService()
