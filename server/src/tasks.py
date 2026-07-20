from src.auth import tasks as auth_tasks
from src.deposit import tasks as deposit_tasks
from src.telegram_log import tasks as telegram_log_tasks
from src.ton_transaction import tasks as ton_transaction_tasks
from src.transaction import tasks as transaction_tasks

__all__ = [
    "auth_tasks",
    "deposit_tasks",
    "telegram_log_tasks",
    "ton_transaction_tasks",
    "transaction_tasks",
]
