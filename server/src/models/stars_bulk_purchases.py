from typing import Any

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.enums import BulkPurchaseStatus
from src.kit.database.models import RecordModel


class StarsBulkPurchase(RecordModel):
    """
    Job record of a stars bulk purchase. Each charged item still gets its own
    Transaction, linked from its item by `transaction_id`.
    """

    __tablename__ = "stars_bulk_purchases"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[BulkPurchaseStatus] = mapped_column(
        Enum(BulkPurchaseStatus, native_enum=False),
        default=BulkPurchaseStatus.pending,
    )
    # Requested input, then per item result. Reassign, never mutate in place.
    items: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
