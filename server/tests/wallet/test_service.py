from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import FragRequestValidationError
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
        valid_until=datetime.now() + timedelta(minutes=3), from_address="", messages=[]
    )

    with pytest.raises(FragRequestValidationError):
        await wallet_service.send_from_tc_transaction(
            session=session,
            wallet_manager=wallet_manager,
            tc_transaction=tc_transaction,
        )
