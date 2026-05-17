from src.exceptions import FragRequestValidationError
from src.kit.ton_connect import TonConnectTransaction


def validate_tc_transaction(tc_transaction: TonConnectTransaction) -> None:
    if len(tc_transaction.messages) != 1:
        raise FragRequestValidationError(
            [
                {
                    "loc": ("transaction", "messages"),
                    "msg": "only one transaction message is required",
                    "type": "value_error",
                    "input": len(tc_transaction.messages),
                }
            ]
        )

    if tc_transaction.messages[0].payload is None:
        raise FragRequestValidationError(
            [
                {
                    "loc": ("transaction", "message", "payload"),
                    "msg": "transaction message must have a payload",
                    "type": "value_error",
                    "input": tc_transaction.messages[0].payload,
                }
            ]
        )
