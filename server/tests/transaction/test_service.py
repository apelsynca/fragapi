from unittest.mock import MagicMock

import pytest
from pytonapi.rest.models import AccountAddress, Message, Transaction
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import FragRequestValidationError
from src.models.transactions import TransactionStatus
from src.transaction.service import transaction as transaction_service


def create_transaction(
    hash: str = "somehash",
    success: bool = True,
    in_msg_type: str = "int_msg",
    value: int = 0,
    destination_address_raw: str
    | None = "0:69061ad51e1cc3626cc4c589088bdcc68ea57f9e6d33c51447c6bf7a200ebc9f",
    out_msgs: list = [],
) -> MagicMock:
    tonapi_transaction = MagicMock(spec=Transaction)
    tonapi_transaction.hash = hash
    tonapi_transaction.lt = 1
    tonapi_transaction.success = success  # test that raises
    tonapi_transaction_in_msg = MagicMock(spec=Message)
    tonapi_transaction_in_msg.msg_type = in_msg_type  # test that raises
    tonapi_transaction_in_msg.value = value
    tonapi_transaction_in_msg.destination = None
    if destination_address_raw is not None:
        tonapi_transaction_in_msg.destination = AccountAddress(
            address=destination_address_raw,
            is_scam=False,
            is_wallet=True,
        )
    tonapi_transaction.in_msg = tonapi_transaction_in_msg
    tonapi_transaction.out_msgs = out_msgs  # test that raises if not len 0

    return tonapi_transaction


@pytest.mark.asyncio
async def test_creates_as_tonapi_internal(session: AsyncSession) -> None:
    tonapi_transaction = create_transaction(
        hash="somehash", success=True, in_msg_type="int_msg", value=425750000
    )

    transaction = await transaction_service.create_as_tonapi_internal(
        session=session, tonapi_transaction=tonapi_transaction
    )

    assert transaction.nano_amount == 425750000
    assert transaction.status == TransactionStatus.completed
    assert (
        transaction.from_wallet
        == "0:69061ad51e1cc3626cc4c589088bdcc68ea57f9e6d33c51447c6bf7a200ebc9f"
    )


@pytest.mark.asyncio
async def test_raises_if_not_success(session: AsyncSession) -> None:
    tonapi_transaction = create_transaction(
        hash="somehash", success=False, in_msg_type="int_msg", value=625750000
    )

    with pytest.raises(FragRequestValidationError):
        await transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )


@pytest.mark.asyncio
async def test_raises_if_wrong_in_msgs_type(session: AsyncSession) -> None:
    tonapi_transaction = create_transaction(
        hash="somehash", success=True, in_msg_type="in_ext_msg", value=125750000
    )

    with pytest.raises(FragRequestValidationError):
        await transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )


@pytest.mark.asyncio
async def test_raises_if_out_msgs(session: AsyncSession) -> None:
    tonapi_transaction = create_transaction(
        hash="somehash",
        success=True,
        in_msg_type="in_ext_msg",
        value=125750000,
        out_msgs=[0],  # does not matter really the type
    )

    with pytest.raises(FragRequestValidationError):
        await transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )


@pytest.mark.asyncio
async def test_must_have_destination(session: AsyncSession) -> None:
    tonapi_transaction = create_transaction(destination_address_raw=None)

    with pytest.raises(FragRequestValidationError):
        await transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )
