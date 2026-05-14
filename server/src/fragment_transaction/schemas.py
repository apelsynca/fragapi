# from datetime import date, datetime
#
# from src.kit.schemas import Schema
# from src.models.transactions import TransactionReason
#
#
# class Transaction(Schema):
#     amount: float
#     reason: TransactionReason
#     message_hash: str | None
#     recipient: str
#     created_at: datetime
#
#
# class TransactionStats(Schema):
#     stars_purchases_count: int  # Количество покупок звезд
#     premium_count: int
#     total_spent: float
#     monthly_spend: float
#     stars_monthly_spend: float
#     premium_monthly_spend: float
#
#
# class TransactionChartPoint(Schema):
#     date: date
#     ton_amount: float
#     transactions_count: int
