from ton_core import Address, Cell, WalletV5Params, to_amount

from src.exceptions import FragRequestValidationError
from src.kit.ton_connect import TonConnectMessage
from src.postgres import AsyncSession
from src.wallet.manager import WalletManager
from src.wallet.types import TonConnectTransaction


class WalletService:
    async def send_from_tc_transaction(
        self,
        session: AsyncSession,
        wallet_manager: WalletManager,
        tc_transaction: TonConnectTransaction,
    ) -> str:
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

        return ext_msg.normalized_hash

    def extract_body(self, message: TonConnectMessage) -> Cell:
        if message.payload is None:
            raise RuntimeError("Omg shiiit")

        padded_payload = message.payload.ljust(4, "=")
        return Cell.one_from_boc(padded_payload)


wallet = WalletService()
