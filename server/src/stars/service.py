import asyncio
import random
import uuid

import structlog

from src.caching import stars_recipient_cache
from src.enums import BulkPurchaseStatus, TransactionReason
from src.exceptions import (
    BadRequest,
    FragError,
    FragRequestValidationError,
    ResourceNotFound,
)
from src.integrations.fragment import Fragment
from src.integrations.fragment.exceptions import (
    FragmentAPIAccessDenied,
    FragmentAPIError,
    FragmentAPINotAUser,
    FragmentAPIUsersNotFound,
)
from src.kit.ton_connect import TonConnectTransaction
from src.logging import Logger
from src.models import StarsBulkPurchase, Transaction, User
from src.postgres import AsyncSession
from src.redis import Redis
from src.stars.schemas import (
    BulkBuyStars,
    BulkBuyStarsItemResult,
    BulkBuyStarsResponse,
    BuyStars,
    BuyStarsResponse,
    StarsRecipient,
)
from src.transaction.models import FTMetadata
from src.transaction.service import transaction as transaction_service

log: Logger = structlog.get_logger()

FRAGMENT_UNAVAILABLE = "Fragment is unavailable, not attempted"


def _item_error(exc: Exception) -> str | None:
    """Why this one item failed, or None when Fragment itself is failing."""
    if isinstance(exc, FragRequestValidationError):
        return "; ".join(error["msg"] for error in exc.errors())
    if isinstance(exc, FragError) and exc.status_code < 500:
        return exc.message
    if isinstance(exc, FragmentAPIError) and not isinstance(
        exc, FragmentAPIAccessDenied
    ):
        return exc.message or "Unknown error from fragment side"
    return None


class StarsService:
    async def buy(
        self,
        session: AsyncSession,
        user: User,
        data: BuyStars,
        fragment: Fragment,
        redis: Redis,
    ) -> BuyStarsResponse:
        recipient_data, tc_transaction = await self._init_buy(
            fragment=fragment, redis=redis, data=data
        )

        transaction = await transaction_service.send_from_tc(
            session=session,
            tc_transaction=tc_transaction,
            user=user,
            reason=TransactionReason.stars,
            metadata=self._metadata(data, recipient_data),
        )

        return self._response(transaction, recipient_data)

    async def create_bulk(
        self, session: AsyncSession, user: User, data: BulkBuyStars
    ) -> StarsBulkPurchase:
        """Saves the batch only. Nothing is charged until `charge_bulk`."""
        bulk = StarsBulkPurchase(
            user_id=user.id,
            status=BulkPurchaseStatus.pending,
            items=[item.model_dump(mode="json") for item in data.items],
        )
        session.add(bulk)
        await session.flush()
        return bulk

    async def get_bulk(
        self, session: AsyncSession, user: User, id: uuid.UUID
    ) -> StarsBulkPurchase:
        bulk = await session.get(StarsBulkPurchase, id)
        if bulk is None or bulk.user_id != user.id:
            raise ResourceNotFound()
        return bulk

    async def charge_bulk(
        self,
        session: AsyncSession,
        bulk: StarsBulkPurchase,
        fragment: Fragment,
        redis: Redis,
    ) -> None:
        """
        Resolves every item against Fragment, then debits the ones the balance
        covers and marks the batch charged, in one commit.
        """
        items = [dict(item) for item in bulk.items]
        # No open DB transaction while talking to Fragment for minutes.
        await session.commit()

        # Sequential: a burst against Fragment is what bulk buying avoids.
        prepared: list[
            tuple[dict, BuyStars, StarsRecipient, TonConnectTransaction]
        ] = []
        fragment_down = False
        for item in items:
            if fragment_down:
                item["error"] = FRAGMENT_UNAVAILABLE
                continue

            data = BuyStars.model_validate(item)
            try:
                recipient_data, tc_transaction = await self._init_buy(
                    fragment=fragment, redis=redis, data=data
                )
            except Exception as exc:
                error = _item_error(exc)
                if error is None:
                    # Fragment itself is failing, the rest would only fail too.
                    log.exception("stars.charge_bulk.fragment_unavailable")
                    fragment_down = True
                    error = FRAGMENT_UNAVAILABLE
                item["error"] = error
            else:
                prepared.append((item, data, recipient_data, tc_transaction))

        await session.refresh(bulk, with_for_update=True)
        if bulk.status != BulkPurchaseStatus.pending:
            # Another delivery of this job charged it while we were resolving.
            await session.commit()
            return

        user = await session.get_one(User, bulk.user_id)
        results = await transaction_service.charge_bulk_from_tc(
            session=session,
            user=user,
            reason=TransactionReason.stars,
            purchases=[
                (tc_transaction, self._metadata(data, recipient_data))
                for _, data, recipient_data, tc_transaction in prepared
            ],
        )
        for (item, _, recipient_data, tc_transaction), result in zip(
            prepared, results, strict=True
        ):
            if isinstance(result, FragError):
                item["error"] = result.message
                continue
            item.update(
                transaction_id=str(result.id),
                message_hash=result.ton_transaction.message_hash,
                amount=result.amount,
                name=recipient_data.name,
                photo=recipient_data.photo,
                tc_transaction=tc_transaction.model_dump(mode="json"),
            )

        bulk.items = items
        bulk.status = BulkPurchaseStatus.charged
        await session.commit()

    def bulk_response(self, bulk: StarsBulkPurchase) -> BulkBuyStarsResponse:
        return BulkBuyStarsResponse(
            id=bulk.id,
            status=bulk.status,
            items=[
                BulkBuyStarsItemResult(
                    username=item["username"],
                    quantity=item["quantity"],
                    error=item.get("error"),
                    result=BuyStarsResponse(
                        message_hash=item["message_hash"],
                        transaction_id=item["transaction_id"],
                        photo=item["photo"],
                        name=item["name"],
                        amount=item["amount"],
                    )
                    if item.get("transaction_id")
                    else None,
                )
                for item in bulk.items
            ],
        )

    async def _init_buy(
        self, fragment: Fragment, redis: Redis, data: BuyStars
    ) -> tuple[StarsRecipient, TonConnectTransaction]:
        log.debug("stars.buy", quantity=data.quantity, username=data.username)

        if len(data.username) < 3:
            raise FragRequestValidationError(
                [
                    {
                        "type": "value_error",
                        "loc": ("body", "username"),
                        "msg": "stars buy request must have a username with length bigger than 3",
                        "input": data.username,
                    }
                ]
            )

        recipient_data = await self.get_recipient(
            fragment=fragment,
            username=data.username,
            quantity=data.quantity,
            redis=redis,
        )
        await asyncio.sleep(0.05)

        buy_request = await fragment.init_buy_stars_request(
            recipient=recipient_data.recipient, quantity=data.quantity
        )
        await asyncio.sleep(0.05)

        buy_link = await fragment.get_buy_stars_link(
            req_id=buy_request.req_id, show_sender=data.show_sender
        )
        log.debug("stars.buy got link", buy_link=buy_link)

        if not buy_link.ok:
            raise FragError("Buy link that we received is invalid")

        return recipient_data, buy_link.transaction

    def _metadata(self, data: BuyStars, recipient_data: StarsRecipient) -> FTMetadata:
        return FTMetadata(
            recipient=recipient_data.recipient,
            recipient_username=data.username,
            stars_amount=data.quantity,
        )

    def _response(
        self, transaction: Transaction, recipient_data: StarsRecipient
    ) -> BuyStarsResponse:
        return BuyStarsResponse(
            message_hash=transaction.ton_transaction.message_hash,
            transaction_id=transaction.id,
            photo=recipient_data.photo,
            name=recipient_data.name,
            amount=transaction.amount,
        )

    async def get_recipient(
        self,
        fragment: Fragment,
        username: str,
        redis: Redis,
        *,
        quantity: int | None = None,
    ) -> StarsRecipient:
        base_recipient = await stars_recipient_cache.get(redis=redis, username=username)

        if base_recipient is not None:
            return StarsRecipient.model_validate(base_recipient)

        try:
            recipient_data = await fragment.search_stars_recipient(
                query=username,
                quantity=random.choice([50, 75, 500, 2500])
                if quantity is None
                else quantity,
            )
        except (FragmentAPIUsersNotFound, FragmentAPINotAUser):
            raise ResourceNotFound("User is not found")
        except FragmentAPIAccessDenied:
            raise FragError(
                "Oops, we somehow lost the access to fragment. "
                "Please wait a little or contact support!"
            )
        except FragmentAPIError as exc:
            log.warning("stars.get_recipient fragment api error", message=exc.message)
            raise BadRequest("Unknown error for us from fragment side")

        recipient = StarsRecipient(
            recipient=recipient_data.found.recipient,
            photo=recipient_data.found.photo,
            name=recipient_data.found.name,
        )

        await stars_recipient_cache.set(
            redis=redis, recipient=recipient, username=username
        )

        return recipient


stars = StarsService()
