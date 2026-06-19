import base64
import re
from unittest.mock import MagicMock

import pytest
from pytonapi.rest.models import Message as TonAPIMessage
from pytonapi.rest.models import Transaction as TonAPITransaction
from ton_core import begin_cell

from src.deposit.ton_payload import TonDepositPayload


def create_tonapi_transaction_mock(
    text: str | None = None, op_name: str = "text_comment"
) -> MagicMock:
    tonapi_transaction = MagicMock(spec=TonAPITransaction, autospec=True)
    in_msg = MagicMock(spec=TonAPIMessage)

    body = {}
    if text is not None:
        body["text"] = text

    in_msg.decoded_body = body
    in_msg.decoded_op_name = op_name
    tonapi_transaction.in_msg = in_msg

    return tonapi_transaction


@pytest.mark.parametrize("ref_hash", ["SomePayload", "And_AOther-WeridPaylo1d"])
def test_generates_ton_ref_hash(ref_hash: str) -> None:
    payload_cell = (
        begin_cell()
        .store_uint(0, 32)
        .store_snake_string(TonDepositPayload.COMMENT_TEMPLATE.format(ref_hash))
        .end_cell()
    )
    payload_boc = payload_cell.to_boc()
    payload = base64.b64encode(payload_boc).decode("utf-8")

    ton_deposit_payload = TonDepositPayload(hash=ref_hash)
    assert ton_deposit_payload.get_base64() == payload


@pytest.mark.parametrize("ref_hash", ["SomePayload", "And_Aother-WeirdPaylo1ad12"])
def test_parses_right_payload(ref_hash: str) -> None:
    tonapi_transaction = create_tonapi_transaction_mock(
        text=TonDepositPayload.COMMENT_TEMPLATE.format(ref_hash)
    )

    ton_deposit_payload = TonDepositPayload.from_tonapi_transaction(tonapi_transaction)
    assert ton_deposit_payload.hash == ref_hash


@pytest.mark.parametrize("op_name", ["wrong_op_name", "text_comment_op"])
def test_from_tonapi_raises_if_wrong_op_name(op_name: str) -> None:
    tonapi_transaction = create_tonapi_transaction_mock(
        text=TonDepositPayload.COMMENT_TEMPLATE.format("someHashie"), op_name=op_name
    )

    with pytest.raises(ValueError, match="op name is not text_comment"):
        TonDepositPayload.from_tonapi_transaction(tonapi_transaction)


def test_from_tonapi_raises_if_no_comment_text() -> None:
    tonapi_transaction = create_tonapi_transaction_mock()
    with pytest.raises(ValueError, match="no comment text"):
        TonDepositPayload.from_tonapi_transaction(tonapi_transaction)


def test_from_tonapi_raises_if_wrong_comment_text() -> None:
    text = "Some kinda right Right text\n\n, but diffie"
    match = re.match(pattern=TonDepositPayload.COMMENT_PATTERN, string=text)
    assert match is None  # needed, cuz what if the text IS the template somehow?

    tonapi_transaction = create_tonapi_transaction_mock(text=text)

    with pytest.raises(ValueError, match="wrong comment text"):
        TonDepositPayload.from_tonapi_transaction(tonapi_transaction)
