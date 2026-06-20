import base64
import re
from typing import Self

from pytonapi.rest.models import Transaction as TonAPITransaction
from ton_core import begin_cell


class TonDepositPayload:
    COMMENT_TEMPLATE = "FragAPI top-up\n\nRef#{}"
    COMMENT_PATTERN = r"[\w\-\ ]+\n\nRef#(.+)"

    def __init__(self, ref_hash: str) -> None:
        self.ref_hash = ref_hash

    def get_base64(self):
        payload_cell = (
            begin_cell()
            .store_uint(0, 32)
            .store_snake_string(
                TonDepositPayload.COMMENT_TEMPLATE.format(self.ref_hash)
            )
            .end_cell()
        )
        payload_boc = payload_cell.to_boc()
        return base64.b64encode(payload_boc).decode("utf-8")

    @classmethod
    def from_tonapi_transaction(cls, tonapi_transaction: TonAPITransaction) -> Self:
        if tonapi_transaction.in_msg is None:
            raise

        if (
            tonapi_transaction.in_msg.decoded_body is None
            or tonapi_transaction.in_msg.decoded_op_name != "text_comment"
        ):
            raise ValueError("op name is not text_comment")

        text = tonapi_transaction.in_msg.decoded_body.get("text", None)
        if not isinstance(text, str) or not text:  # string + non-empty
            raise ValueError("no comment text")

        match = re.match(pattern=cls.COMMENT_PATTERN, string=text)
        if match is None:
            raise ValueError("wrong comment text")

        return cls(ref_hash=match.group(1))
