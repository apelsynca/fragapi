import asyncio

from src.tonapi.service import tonapi as tonapi_service


async def main() -> None:
    tx_hash = input("Transaction hash: ").strip()
    transaction = await tonapi_service.get_blockchain_transaction(tx_hash=tx_hash)

    print(transaction)


if __name__ == "__main__":
    asyncio.run(main())
