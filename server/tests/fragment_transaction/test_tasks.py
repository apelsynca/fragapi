import uuid
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from pytest_mock import MockerFixture
from ton_core import Address, Cell, WalletV5Params, to_nano
from tonutils.contracts import WalletV5R1

from src.exceptions import BadRequest, FragRequestValidationError, ResourceNotFound
from src.fragment_transaction.tasks import process_fragment_transaction
from src.kit.ton_connect import TonConnectMessage, TonConnectTransaction
from src.models import FragmentTransaction, User
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import (
    create_fragment_transaction,
    create_transaction,
    rstr,
)
from tests.fixtures.worker import FakeWalletManager


@pytest_asyncio.fixture
async def valid_frag_trans(
    save_fixture: SaveFixture, valid_tc_transaction_hash: str, user: User
) -> FragmentTransaction:
    transaction = await create_transaction(
        save_fixture,
        message_hash=valid_tc_transaction_hash,
    )
    return await create_fragment_transaction(
        save_fixture, user=user, transaction=transaction
    )


@pytest.mark.asyncio
async def test_process_transaction_raises_if_not_found(
    valid_tc_transaction: TonConnectTransaction,
) -> None:
    with pytest.raises(ResourceNotFound):
        await process_fragment_transaction(
            fragment_transaction_id=uuid.uuid4(), tc_transaction=valid_tc_transaction
        )


@pytest.mark.asyncio
async def test_process_raises_if_transaction_msg_hash_differ_from_tc_transaction(
    save_fixture: SaveFixture, valid_tc_transaction: TonConnectTransaction, user: User
) -> None:
    transaction = await create_transaction(
        save_fixture, message_hash=rstr("completely-wrong-hash")
    )
    frag_trans = await create_fragment_transaction(
        save_fixture, user=user, transaction=transaction
    )

    with pytest.raises(BadRequest):
        await process_fragment_transaction(
            fragment_transaction_id=frag_trans.id, tc_transaction=valid_tc_transaction
        )


@pytest.mark.asyncio
async def test_process_raises_if_tc_msg_len_diff(
    valid_tc_transaction: TonConnectTransaction,
    valid_frag_trans: FragmentTransaction,
) -> None:
    valid_tc_transaction.messages.append(
        TonConnectMessage(address="", amount=0, payload="")
    )

    with pytest.raises(BadRequest):
        await process_fragment_transaction(
            fragment_transaction_id=valid_frag_trans.id,
            tc_transaction=valid_tc_transaction,
        )


@pytest.mark.asyncio
async def test_process_calls_transfer(
    wallet_manager: FakeWalletManager,
    valid_tc_transaction: TonConnectTransaction,
    valid_frag_trans: FragmentTransaction,
) -> None:
    # Given
    tc_msg = valid_tc_transaction.messages[0]
    assert tc_msg.payload is not None

    wallet_manager.balance = to_nano(25.2)
    mma = MagicMock()
    mma.normalized_hash = "anyhash"
    wallet_manager.wallet.transfer.return_value = mma

    # When
    await process_fragment_transaction(
        fragment_transaction_id=valid_frag_trans.id,
        tc_transaction=valid_tc_transaction,
    )

    # Then
    padded_payload = tc_msg.payload + "=" * (-len(tc_msg.payload) % 4)
    body = Cell.one_from_boc(padded_payload)

    assert wallet_manager.amounts_log == [tc_msg.amount]
    wallet_manager.wallet.transfer.assert_called_once_with(
        destination=Address(tc_msg.address),
        body=body,
        amount=tc_msg.amount,
        params=WalletV5Params(
            valid_until=int(valid_tc_transaction.valid_until.timestamp()) + 10
        ),
    )


@pytest.mark.asyncio
async def test_process_calls_validate_transaction(
    valid_tc_transaction: TonConnectTransaction,
    valid_frag_trans: FragmentTransaction,
    mocker: MockerFixture,
    wallet_manager: FakeWalletManager,
) -> None:
    mock = mocker.patch(
        "src.fragment_transaction.tasks.validate_tc_transaction",
        side_effect=FragRequestValidationError([]),
    )

    with pytest.raises(FragRequestValidationError):
        await process_fragment_transaction(
            fragment_transaction_id=valid_frag_trans.id,
            tc_transaction=valid_tc_transaction,
        )

    mock.assert_called_once_with(tc_transaction=valid_tc_transaction)
    wallet_manager.wallet.transfer.assert_not_called()


@pytest.mark.asyncio
async def test_process_sets_hash(
    valid_tc_transaction: TonConnectTransaction,
    valid_frag_trans: FragmentTransaction,
    wallet_manager: FakeWalletManager,
) -> None:
    # TODO: ext_msg.normalized_hash replace with tonapi

    m = MagicMock(spec=WalletV5R1)
    hs = rstr("somehash")
    m.normalized_hash = hs
    wallet_manager.wallet.transfer.return_value = m

    # Given
    assert valid_frag_trans.transaction.hash is None

    # When
    await process_fragment_transaction(
        fragment_transaction_id=valid_frag_trans.id,
        tc_transaction=valid_tc_transaction,
    )

    # Then
    # return mock value
    assert valid_frag_trans.transaction.hash == hs


@pytest.mark.asyncio
async def test_process_calls_log(
    valid_tc_transaction: TonConnectTransaction,
    valid_frag_trans: FragmentTransaction,
) -> None:
    # NOTE: logggggg

    # Given

    # When

    # Then
    # send_telegram_log.assert_called_once(valid_frag_trans.id)
    pass
