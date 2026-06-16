import asyncio
import random
from datetime import timedelta

from ton_core import Address, ExternalMessage, to_nano

from src.kit.ton_connect import TonConnectMessage, TonConnectTransaction
from src.kit.utils import utc_now
from tests.fixtures.random_objects import RANDOM_TON_ADDRESSES

TON_ADDR = "UQANtyTiJuWgo5cTdrVlzpTzhYD3Heg3ssPoeAW2dM2v6nR1"


async def main() -> None:
    tc_trans = TonConnectTransaction(
        valid_until=utc_now() + timedelta(seconds=10),
        from_address=Address(random.choice(RANDOM_TON_ADDRESSES)).to_str(
            is_user_friendly=True
        ),
        messages=[
            TonConnectMessage(
                address=TON_ADDR,
                amount=to_nano(5.25),
                payload="te6ccgEBAQEAJwAASgAAAAA1MCBUZWxlZ3JhbSBTdGFycyAKClJlZiN4Z01NbTM3bVY",
            )
        ],
    )

    tc_msg = tc_trans.messages[0]

    message = ExternalMessage(
        dest=Address(tc_msg.address), body=tc_msg.get_payload_cell()
    )

    print(message.normalized_hash)


if __name__ == "__main__":
    asyncio.run(main())
