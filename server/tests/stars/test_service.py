from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import FragError
from src.fragment_transaction.models import FTMetadata
from src.fragment_transaction.service import FragmentTransactionService
from src.integrations.fragment.types import (
    BuyLink,
    FoundRecipientData,
    RecipientData,
)
from src.kit.ton_connect import TonConnectTransaction
from src.models import User
from src.models.fragment_transactions import (
    FragmentTransactionReason,
)
from src.stars.schemas import BuyStars
from src.stars.service import stars as stars_service
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import (
    create_fragment_transaction,
    create_transaction,
)


@pytest.fixture(autouse=True)
def fragment_transaction_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(
        "src.stars.service.fragment_transaction_service",
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
    fragment.search_stars_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="", name=""
        ),
    )
    fragment.get_buy_stars_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )
    transaction = await create_transaction(
        save_fixture,
        message_hash="vaid",
    )

    fragment_transaction_service.send_from_tc.return_value = (
        await create_fragment_transaction(
            save_fixture, user=user, transaction=transaction
        )
    )

    await stars_service.buy(
        session=session,
        user=user,
        data=BuyStars(username="homocitrus", quantity=52),
        fragment=fragment,
    )

    fragment_transaction_service.send_from_tc.assert_called_once_with(
        session=session,
        tc_transaction=valid_tc_transaction,
        user=user,
        reason=FragmentTransactionReason.stars,
        metadata=FTMetadata(
            recipient="SomeMtDataXx", recipient_username="homocitrus", stars_amount=52
        ),
    )


@pytest.mark.asyncio
async def test_buy_raises_if_link_is_false(
    session: AsyncSession,
    user: User,
    fragment: MagicMock,
    valid_tc_transaction: TonConnectTransaction,
) -> None:
    fragment.search_stars_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="", name=""
        ),
    )
    fragment.get_buy_stars_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=False
    )

    with pytest.raises(FragError):
        await stars_service.buy(
            session=session,
            user=user,
            data=BuyStars(username="homocitrus", quantity=52),
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
    fragment.search_stars_recipient.return_value = RecipientData(
        ok=True,
        found=FoundRecipientData(
            myself=True, recipient="SomeMtDataXx", photo="the photo", name="TheName"
        ),
    )
    fragment.get_buy_stars_link.return_value = BuyLink(
        transaction=valid_tc_transaction, ok=True
    )

    transaction = await create_transaction(
        save_fixture,
        message_hash="myhash",
    )
    frag_trans = await create_fragment_transaction(
        save_fixture, user=user, transaction=transaction
    )

    fragment_transaction_service.send_from_tc.return_value = frag_trans

    # AAA
    stars_buy_response = await stars_service.buy(
        session=session,
        user=user,
        data=BuyStars(username="homocitrus", quantity=52),
        fragment=fragment,
    )

    assert stars_buy_response.message_hash == "myhash"
    assert stars_buy_response.transaction_id == frag_trans.id
    assert stars_buy_response.photo == "the photo"
    assert stars_buy_response.name == "TheName"
    assert stars_buy_response.amount is not None
