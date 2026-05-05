from sqlalchemy.ext.asyncio import AsyncSession

from src.enums import PremiumMonths
from src.exceptions import FragError, InsuficcientFunds, ResourceNotFound
from src.fee import after_fee, after_ton_network_fee
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.rest import FragmentRest
from src.premium.schemas import PremiumRecipient
from src.users.repository import UserRepository


class PremiumService:
    async def buy(
        self,
        session: AsyncSession,
        fragment_rest: FragmentRest,
        user_id: int,
        username: str,
        months: PremiumMonths,
    ):
        # probably will need to lock user, so that no race conditions happen
        recipient_data = await self.get_recipient(fragment_rest, username=username)
        buy_request = await fragment_rest.init_gift_premium_request(
            recipient=recipient_data.recipient, months=months.value
        )

        premium_price = after_ton_network_fee(after_fee(buy_request.amount))

        user = await UserRepository.from_session(session).get_by_id_for_update(
            id=user_id
        )
        if user is None:
            raise FragError()

        if premium_price > user.balance:
            raise InsuficcientFunds("Not enough balance")

        user.balance -= premium_price

    async def get_recipient(
        self,
        fragment_rest: FragmentRest,
        username: str,
    ) -> PremiumRecipient:
        try:
            recipient = await fragment_rest.search_premium_gift_recipient(
                query=username
            )
        except FragmentAPIUsersNotFound:
            raise ResourceNotFound("User is not found")

        return PremiumRecipient(
            recipient=recipient.found.recipient,
            photo=recipient.found.photo,
            name=recipient.found.name,
        )


premium = PremiumService()
