from ton_core import Address, Cell, NetworkGlobalID, WalletV5Params
from ton_core.boc.deserialize import BocError
from tonutils.contracts import WalletV5R1

from src.config import settings
from src.exceptions import BadRequest
from src.wallet.types import TonConnectTransaction

if settings.is_production():
    env_network_id = NetworkGlobalID.MAINNET
else:
    env_network_id = NetworkGlobalID.TESTNET


class WalletService:
    async def transfer_from_tc(
        self, wallet: WalletV5R1, transaction: TonConnectTransaction
    ) -> str:
        if len(transaction.messages) > 1:
            raise BadRequest("Multiple messages transfer is not supported")

        message = transaction.messages[0]
        address = Address(message.address)
        body = None

        if message.payload is not None:
            padded_payload = message.payload + "=" * (
                ((4 - len(message.payload)) % 4) % 4
            )
            try:
                body = Cell.one_from_boc(padded_payload)
            except BocError:
                raise BadRequest("Invalid transaction payload")

        valid_until = int(transaction.valid_until.timestamp()) + 10

        ext_msg = await wallet.transfer(
            destination=address,
            amount=message.amount,
            body=body,
            params=WalletV5Params(valid_until=valid_until),
        )

        return ext_msg.normalized_hash

    async def get_balance(self, wallet: WalletV5R1) -> float:
        await wallet.refresh()
        return wallet.balance

    async def process_webhook(self) -> None:
        pass


wallet = WalletService()
