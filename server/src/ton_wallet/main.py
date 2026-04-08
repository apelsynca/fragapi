from datetime import datetime

from pytoniq_core import Address, Cell
from tonutils.clients import ToncenterClient
from tonutils.contracts import WalletV5Params
from tonutils.contracts import WalletV5R1 as _Wallet
from tonutils.utils import to_amount

from src.config import settings

from .types import TonConnectMessage


class WalletV5R1(_Wallet):
    async def get_real_ton_balance(self) -> float:
        await self.client.connect()
        await self.refresh()
        return float(to_amount(self.balance))

    async def transfer_from_tc(
        self, message: TonConnectMessage, valid_until: datetime
    ) -> str:
        body = None

        if message.payload:
            padded_payload = message.payload + "=" * (
                ((4 - len(message.payload)) % 4) % 4
            )
            body = Cell.one_from_boc(padded_payload)

        ext_msg = await self.transfer(
            destination=Address(message.address),
            amount=message.amount,
            body=body,
            params=WalletV5Params(valid_until=int(valid_until.timestamp())),
        )

        return ext_msg.normalized_hash


client = ToncenterClient(
    network=settings.get_env_network_id(),
    api_key=settings.toncenter_api_key.get_secret_value(),
)


def get_wallet() -> WalletV5R1:
    wallet, *_ = WalletV5R1.from_mnemonic(
        client=client,  # pyright: ignore
        mnemonic=settings.get_secret_wallet_mnemonic(),
    )

    return wallet


wallet = get_wallet()
