from src.auth import tasks as auth_tasks
from src.backoffice.telegram_logs import tasks as backoffice_tg_logs_tasks
from src.fragment_transaction import tasks as fragment_transaction_tasks
from src.telegram_log import tasks as telegram_log_tasks

__all__ = [
    "auth_tasks",
    "backoffice_tg_logs_tasks",
    "fragment_transaction_tasks",
    "telegram_log_tasks",
]
