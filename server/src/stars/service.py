import random

from sqlalchemy.ext.asyncio import AsyncSession
from ton_core import to_amount

from src.exceptions import (
    BadRequest,
    FragError,
    FragRequestValidationError,
    InsuficcientFunds,
    ResourceNotFound,
)
from src.fee import TON_FEE, after_fee, after_ton_network_fee
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.rest import FragmentRest
from src.logging import get_logger
from src.models import User
from src.stars.schemas import StarsRecipient
from src.users.repository import UserRepository
from src.wallet.manager import WalletManager
from src.wallet.types import TonConnectTransaction

log = get_logger()


class StarsService:
    async def get_buy_tc_transaction(
        self, fragment_rest: FragmentRest, username: str, quantity: int
    ) -> TonConnectTransaction:
        if quantity < 50 or quantity > 10_000_000:
            raise BadRequest("Invalid quantity")

        recipient_data = await self.get_recipient(fragment_rest, username=username)

        buy_request = await fragment_rest.init_buy_stars_request(
            recipient=recipient_data.recipient, quantity=quantity
        )

        buy_link = await fragment_rest.get_buy_stars_link(
            req_id=buy_request.req_id, show_sender=False
        )

        return buy_link.transaction

    async def buy_from_transaction(
        self,
        session: AsyncSession,
        user: User,
        wallet_manager: WalletManager,
        transaction: TonConnectTransaction,
    ) -> str:
        if len(transaction.messages) != 1:
            raise FragRequestValidationError(
                [
                    {
                        "loc": ("transaction", "messages"),
                        "msg": "only one transaction message is required",
                        "type": "value_error",
                        "input": None,
                    }
                ]
            )

        if transaction.messages[0].payload is None:
            raise FragRequestValidationError(
                [
                    {
                        "loc": ("transaction", "message", "payload"),
                        "msg": "transaction message must have a payload",
                        "type": "value_error",
                        "input": None,
                    }
                ]
            )

        stars_price_on_fragment = float(to_amount(transaction.messages[0].amount))
        stars_price = after_ton_network_fee(after_fee(stars_price_on_fragment))

        wallet_balance = await wallet_manager.get_balance()
        if wallet_balance < stars_price_on_fragment + TON_FEE:
            raise FragError("FragAPI internal wallet balance is too low!")

        user_repository = UserRepository.from_session(session)
        # WARN: im not sure whether it is not HACKABLE!!!!
        await user_repository.get_by_id_for_update(id=user.id)

        if user.balance <= stars_price:
            raise InsuficcientFunds()

        user.balance -= stars_price

        return await wallet_manager.transfer_from_tc(transaction=transaction)

    async def get_recipient(
        self, fragment_rest: FragmentRest, username: str, *, quantity: int | None = None
    ) -> StarsRecipient:
        try:
            recipient = await fragment_rest.search_stars_recipient(
                query=username,
                quantity=random.choice([50, 75, 500, 2500])
                if quantity is None
                else quantity,
            )
        except FragmentAPIUsersNotFound:
            raise ResourceNotFound("User is not found")

        return StarsRecipient(
            recipient=recipient.found.recipient,
            photo=recipient.found.photo,
            name=recipient.found.name,
        )

    async def get_single_star_price(self) -> float:
        return 0

    async def get_price(self, quantity: int):
        if quantity < 50 or quantity > 10_000_000:
            raise BadRequest("Invalid quantity")


stars = StarsService()
