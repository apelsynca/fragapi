from fastapi import Request
from ton_core import NetworkGlobalID
from tonutils.clients import ToncenterClient
from tonutils.contracts import WalletV5R1

from src.config import settings

toncenter = ToncenterClient(
    network=NetworkGlobalID.TESTNET, api_key=settings.TONCENTER_API_KEY
)


def create_wallet():
    wallet, *_ = WalletV5R1.from_mnemonic(
        client=toncenter,  # pyright: ignore
        mnemonic=settings.WALLET_MNEMONIC,
    )
    return wallet


def get_wallet(request: Request) -> WalletV5R1:
    return request.state.wallet
