# from ton_core import Transaction
#
# from src.config import settings
# from src.exceptions import ResourceNotFound

# from .main import client as toncenter_client


# class TransactionNotFound(ResourceNotFound):
#     def __init__(self, message: str = "Transaction not found"):
#         super().__init__(message)

#
# async def get_transaction(tx_hash: str, lt: int, limit: int = 1) -> Transaction:
#     async with toncenter_client:
#         transactions = await toncenter_client.get_transactions(
#             address=settings.ton_address, limit=limit, from_lt=lt
#         )
#         if len(transactions) == 0:
#             raise TransactionNotFound
#
#         tx = transactions[0]
#
#         if tx.cell.hash.hex() != tx_hash:
#             raise TransactionNotFound
#         if tx.lt != lt:
#             raise TransactionNotFound
#
#         return tx
