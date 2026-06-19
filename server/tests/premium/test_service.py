from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.enums import PremiumMonths, TransactionReason
from src.exceptions import FragError, ResourceNotFound
from src.integrations.fragment.exceptions import FragmentAPIUsersNotFound
from src.integrations.fragment.types import (
    BuyLink,
    FoundRecipientData,
    RecipientData,
)
from src.kit.ton_connect import TonConnectTransaction
from src.models import User
from src.postgres import AsyncSession
from src.premium.schemas import BuyPremium
from src.premium.service import premium as premium_service
from src.transaction.models import FTMetadata
from src.transaction.service import FragmentTransactionService
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import (
    create_fragment_transaction,
    create_ton_transaction,
)


@pytest.fixture(autouse=True)
def fragment_transaction_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.premium.service.fragment_transaction_service",
        spec=FragmentTransactionService,
    )


@pytest.mark.asyncio
async def test_buy_calls_frag_service_buy_from_tc(
    save_fixture: SaveFixture,
    session: AsyncSession,
    user: User,
    fragment: MagicMock,
    valid_tc_transaction: TonConnectTransaction,
    fragment_transaction_service: MagicMock,
) -> None:
    fragment.search_premium_gift_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="", name=""
        ),
    )
    fragment.get_gift_premium_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )
    transaction = await create_ton_transaction(
        save_fixture,
        message_hash="vaid",
    )

    fragment_transaction_service.send_from_tc.return_value = (
        await create_fragment_transaction(
            save_fixture, user=user, transaction=transaction
        )
    )

    await premium_service.buy(
        session=session,
        user=user,
        data=BuyPremium(username="homocitrus", months=PremiumMonths.SIX_MONTHS),
        fragment=fragment,
    )

    fragment_transaction_service.send_from_tc.assert_called_once_with(
        session=session,
        tc_transaction=valid_tc_transaction,
        user=user,
        reason=TransactionReason.premium,
        metadata=FTMetadata(
            recipient="SomeMtDataXx", recipient_username="homocitrus", premium_months=6
        ),
    )


@pytest.mark.asyncio
async def test_buy_raises_if_link_is_false(
    session: AsyncSession,
    user: User,
    fragment: MagicMock,
    valid_tc_transaction: TonConnectTransaction,
) -> None:
    fragment.search_premium_gift_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="", name=""
        ),
    )
    fragment.get_gift_premium_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=False
    )

    with pytest.raises(FragError):
        await premium_service.buy(
            session=session,
            user=user,
            data=BuyPremium(username="homocitrus", months=PremiumMonths.YEAR),
            fragment=fragment,
        )


@pytest.mark.asyncio
async def test_buy_returns_good(
    save_fixture: SaveFixture,
    session: AsyncSession,
    user: User,
    fragment: MagicMock,
    valid_tc_transaction: TonConnectTransaction,
    fragment_transaction_service: MagicMock,
) -> None:
    fragment.search_premium_gift_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="the photo", name="TheName"
        ),
    )
    fragment.get_gift_premium_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )

    transaction = await create_ton_transaction(
        save_fixture,
        message_hash="myhash",
    )
    frag_trans = await create_fragment_transaction(
        save_fixture, user=user, transaction=transaction
    )

    fragment_transaction_service.send_from_tc.return_value = frag_trans

    # When
    prem_buy_response = await premium_service.buy(
        session=session,
        user=user,
        data=BuyPremium(username="homocitrus", months=PremiumMonths.THREE_MONTHS),
        fragment=fragment,
    )

    assert prem_buy_response.message_hash == "myhash"
    assert prem_buy_response.transaction_id == frag_trans.id
    assert prem_buy_response.photo == "the photo"
    assert prem_buy_response.name == "TheName"
    assert prem_buy_response.amount is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("username", ["someusername", "literrally_Anyusername"])
async def test_get_recipient_raises_if_fragment_not_found(
    fragment: MagicMock, username: str
) -> None:
    fragment.search_premium_gift_recipient.side_effect = FragmentAPIUsersNotFound()
    with pytest.raises(ResourceNotFound):
        await premium_service.get_recipient(fragment=fragment, username=username)
