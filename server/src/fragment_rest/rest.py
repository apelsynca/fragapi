from src.fragment_rest.base_rest import BaseFragmentRest
from src.fragment_rest.types import FragmentRecipientData


class FragmentRest(BaseFragmentRest):
    async def search_stars_recipient(
        self, query: str, quantity: int | None = None
    ) -> FragmentRecipientData:
        resp = await self._request(
            method="searchStarsRecipient",
            data={"query": query, "quantity": quantity if quantity is not None else ""},
        )

        return FragmentRecipientData.model_validate(resp)
