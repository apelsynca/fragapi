from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import ExternalMessage, to_nano

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
    mm = MagicMock(spec=ExternalMessage)
    mm.normalized_hash = "mymsghash"
    wallet.transfer.return_value = mm

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

    transaction = await wallet_service.send_from_tc_transaction(
        session=session, wallet_manager=wallet_manager, tc_transaction=tc_transaction
    )

    assert transaction.message_hash == "mymsghash"
