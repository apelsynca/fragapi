from src.exceptions import ResourceNotFound
from src.fragment_rest.exceptions import FragmentAPIUsersNotFound
from src.fragment_rest.rest import FragmentRest
from src.premium.schemas import PremiumRecipient


class PremiumService:
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
