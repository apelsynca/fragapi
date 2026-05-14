import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import FragRequestValidationError
from src.transaction.service import transaction as transaction_service
from tests.fixtures.random_objects import create_tonapi_transaction_mock


@pytest.mark.asyncio
async def test_creates_as_tonapi_internal(session: AsyncSession) -> None:
    tonapi_transaction = create_tonapi_transaction_mock(
        hash="somehash",
        success=True,
        in_msg_type="int_msg",
        value=425750000,
        source_address_raw="0:11111ad51e1cc3626cc4c589088bdcc68ea57f9e6d33c51447c6bf7a200ebxxx",
    )

    transaction = await transaction_service.create_as_tonapi_internal(
        session=session, tonapi_transaction=tonapi_transaction
    )

    assert transaction.nano_amount == 425750000
    assert (
        transaction.to_address
        == "0:69061ad51e1cc3626cc4c589088bdcc68ea57f9e6d33c51447c6bf7a200ebc9f"
    )
    assert (
        transaction.from_address
        == "0:11111ad51e1cc3626cc4c589088bdcc68ea57f9e6d33c51447c6bf7a200ebxxx"
    )


@pytest.mark.asyncio
async def test_tonapi_raises_if_not_success(session: AsyncSession) -> None:
    tonapi_transaction = create_tonapi_transaction_mock(
        hash="somehash", success=False, in_msg_type="int_msg", value=625750000
    )

    with pytest.raises(FragRequestValidationError):
        await transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )


@pytest.mark.asyncio
async def test_tonapi_raises_if_wrong_in_msgs_type(session: AsyncSession) -> None:
    tonapi_transaction = create_tonapi_transaction_mock(
        hash="somehash", success=True, in_msg_type="in_ext_msg", value=125750000
    )

    with pytest.raises(FragRequestValidationError):
        await transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )


@pytest.mark.asyncio
async def test_tonapi_raises_if_out_msgs(session: AsyncSession) -> None:
    tonapi_transaction = create_tonapi_transaction_mock(
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
async def test_tonapi_must_have_destination(session: AsyncSession) -> None:
    tonapi_transaction = create_tonapi_transaction_mock(destination_address_raw=None)

    with pytest.raises(FragRequestValidationError):
        await transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )


@pytest.mark.asyncio
async def test_raises_wrong_dests_if_source_is_none(
    session: AsyncSession,
) -> None:
    tonapi_transaction = create_tonapi_transaction_mock(source_address_raw=None)

    with pytest.raises(FragRequestValidationError):
        await transaction_service.create_as_tonapi_internal(
            session=session, tonapi_transaction=tonapi_transaction
        )
