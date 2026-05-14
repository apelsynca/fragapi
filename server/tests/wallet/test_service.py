from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import to_nano

from src.exceptions import FragRequestValidationError
from src.kit.ton_connect import TonConnectMessage
from src.wallet.manager import WalletManager
from src.wallet.service import wallet as wallet_service
from src.wallet.types import TonConnectTransaction


@pytest.mark.asyncio
async def test_raises_send_from_tc_transaction(
    session: AsyncSession, wallet_manager: WalletManager
) -> None:
    tc_transaction = TonConnectTransaction(
        valid_until=datetime.now() + timedelta(minutes=3), from_address="", messages=[]
    )

    with pytest.raises(FragRequestValidationError):
        await wallet_service.send_from_tc_transaction(
            session=session,
            wallet_manager=wallet_manager,
            tc_transaction=tc_transaction,
        )


@pytest.mark.asyncio
async def test_requires_payload(
    session: AsyncSession, wallet_manager: WalletManager
) -> None:
    tc_transaction = TonConnectTransaction(
        valid_until=datetime.now() + timedelta(minutes=3),
        from_address="",
        messages=[TonConnectMessage(address="", amount=0, payload=None)],
    )

    with pytest.raises(FragRequestValidationError):
        await wallet_service.send_from_tc_transaction(
            session=session,
            wallet_manager=wallet_manager,
            tc_transaction=tc_transaction,
        )


@pytest.mark.asyncio
async def test_creates_transaction_after_transfer_with_right_message_hash(
    session: AsyncSession, wallet_manager: WalletManager, wallet: MagicMock
) -> None:
    wallet.balance = to_nano(10)

    tc_transaction = TonConnectTransaction(
        valid_until=datetime.now() + timedelta(minutes=3),
        from_address="0:xxxxxxxxxx",  # NOTE: dont care for now
        messages=[
            TonConnectMessage(
                address="0:69061ad51e1cc3626cc4c589088bdcc68ea57f9e6d33c51447c6bf7a200ebc9f",
                amount=to_nano(9.25),
                payload="te6ccgEBAQEAKAAATAAAAAA1MDAgVGVsZWdyYW0gU3RhcnMgCgpSZWYjQ1Bxb0JpdlVQ",
            )
        ],
    )

    message_hash = await wallet_service.send_from_tc_transaction(
        session=session, wallet_manager=wallet_manager, tc_transaction=tc_transaction
    )

    # maybe build here the msg myself
    assert message_hash is not None  # TODO: and that way to calculate msg hash


# kinda a wallet manager thing
# @pytest.mark.asyncio
# async def test_what_if_balance_is_low() -> None:
#     pass
