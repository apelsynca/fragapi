import asyncio

from ton_core import Cell, NetworkGlobalID

from src.config import settings
from src.wallet.ton import create_toncenter


async def main() -> None:
    toncenter = create_toncenter(network=NetworkGlobalID.MAINNET)

    address = input("TON Address (from env by default): ") or settings.TON_ADDRESS

    LIMIT = 10
    print(f"Searching transactions with limit - {LIMIT}")

    async with toncenter:
        bc_trans_result = await toncenter.provider.get_transactions(
            address=address, limit=LIMIT
        )
        if bc_trans_result.result is None:
            print("No transactions found.")
            return

        for i, bc_trans in enumerate(bc_trans_result.result):
            if bc_trans.data is None:
                continue

            tx_hash = Cell.one_from_boc(bc_trans.data).hash.hex()

            print(f"{i} - https://tonscan.org/tx/{tx_hash}")


if __name__ == "__main__":
    asyncio.run(main())
