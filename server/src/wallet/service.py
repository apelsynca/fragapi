from ton_core import Address, Cell, WalletV5Params, to_amount

from src.exceptions import FragRequestValidationError
from src.kit.ton_connect import TonConnectMessage
from src.models import Transaction  # maybe bad decision
from src.postgres import AsyncSession
from src.transaction.service import transaction as transaction_service
from src.wallet.manager import WalletManager
from src.wallet.types import TonConnectTransaction


class WalletService:
    async def send_from_tc_transaction(
        self,
        session: AsyncSession,
        wallet_manager: WalletManager,
        tc_transaction: TonConnectTransaction,
    ) -> Transaction:
        """
        Validate that message is right
        Create pending transaction in db

        """

        if len(tc_transaction.messages) != 1:
            raise FragRequestValidationError(
                [
                    {
                        "loc": ("transaction", "messages"),
                        "msg": "only one transaction message is required",
                        "type": "value_error",
                        "input": len(tc_transaction.messages),
                    }
                ]
            )

        if tc_transaction.messages[0].payload is None:
            raise FragRequestValidationError(
                [
                    {
                        "loc": ("transaction", "message", "payload"),
                        "msg": "transaction message must have a payload",
                        "type": "value_error",
                        "input": tc_transaction.messages[0].payload,
                    }
                ]
            )

        message = tc_transaction.messages[0]

        wallet = await wallet_manager.get_wallet_for_amount(
            amount=float(to_amount(message.amount))  # NOTE: redo maybe to just amount
        )

        body = self.extract_body(message=message)

        valid_until = int(tc_transaction.valid_until.timestamp()) + 10
        ext_msg = await wallet.transfer(
            destination=Address(message.address),
            body=body,
            amount=message.amount,
            params=WalletV5Params(valid_until=valid_until),
        )
        message_hash = ext_msg.normalized_hash

        return await transaction_service.create_as_tc(
            session=session,
            nano_amount=message.amount,
            message_hash=message_hash,
            from_address=wallet.address.to_str(is_user_friendly=False),
            to_address=message.address,
        )

    def extract_body(self, message: TonConnectMessage) -> Cell:
        if message.payload is None:
            raise RuntimeError("Omg shiiit")

        padded_payload = message.payload + "=" * (-len(message.payload) % 4)
        return Cell.one_from_boc(padded_payload)


wallet = WalletService()
