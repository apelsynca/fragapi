from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.enums import PremiumMonths
from src.exceptions import FragError, InsuficcientFunds, ResourceNotFound
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.types import BuyRequest
from src.models import User
from src.premium.service import premium as premium_service
from src.wallet.manager import WalletManager
from tests.fixtures.random_objects import get_fake_recipient_data, rstr


@pytest.mark.asyncio
async def test_raises_if_not_enough_balance(
    session: AsyncSession,
    fragment_rest: MagicMock,
    wallet_manager: WalletManager,
    user: User,
) -> None:
    fragment_rest.search_premium_gift_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_gift_premium_request.return_value = BuyRequest(
        req_id=rstr("some"), myself=False, amount=123
    )

    assert user.balance == 0

    with pytest.raises(InsuficcientFunds):
        await premium_service.buy(
            session=session,
            fragment_rest=fragment_rest,
            wallet_manager=wallet_manager,
            user_id=user.id,
            username="",
            months=PremiumMonths.SIX_MONTHS,
        )


@pytest.mark.asyncio
async def test_buy_creates_transaction(
    session: AsyncSession, fragment_rest: MagicMock, user: User
) -> None:
    # await premium_service.buy(
    #     session, fragment_rest, user=user, username="", months=PremiumMonths.SIX_MONTHS
    # )
    pass


@pytest.mark.asyncio
async def test_get_recipient_raises_when_not_found(fragment_rest: MagicMock) -> None:
    fragment_rest.search_premium_gift_recipient.side_effect = FragmentAPIUsersNotFound

    with pytest.raises(ResourceNotFound):
        await premium_service.get_recipient(fragment_rest, username="")


@pytest.mark.asyncio
async def test_buy_raises_if_user_not_found(
    session: AsyncSession, fragment_rest: MagicMock, wallet_manager: MagicMock
) -> None:
    fragment_rest.search_premium_gift_recipient.return_value = get_fake_recipient_data()
    fragment_rest.init_gift_premium_request.return_value = BuyRequest(
        req_id=rstr("someid"), myself=False, amount=123.52
    )

    with pytest.raises(FragError):
        await premium_service.buy(
            session=session,
            fragment_rest=fragment_rest,
            wallet_manager=wallet_manager,
            user_id=291529,
            username="doesnotmatter",
            months=PremiumMonths.SIX_MONTHS,
        )


@pytest.mark.asyncio
async def test_caches_premium_ton_prices() -> None:
    pass


@pytest.mark.asyncio
async def test_gets_prices_from_cache() -> None:
    pass
