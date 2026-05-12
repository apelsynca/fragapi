from src.fragment.rest_client import FragmentRestClient
from src.fragment.types import RecipientData


class Fragment:
    def __init__(self, clients: list[FragmentRestClient]) -> None:
        if len(clients) == 0:
            raise RuntimeError("Fragment needs at least 1 client")

        self.clients = clients

    async def search_stars_recipient(
        self, query: str, quantity: int | None = None
    ) -> RecipientData:
        client = self.get_client()

        data = await client.api_request(
            method="searchStarsRecipient",
            data={
                "query": query,
                "quantity": str(quantity) if quantity is not None else "",
            },
        )

        return RecipientData.model_validate(data)

    def get_client(self) -> FragmentRestClient:
        # TODO: normal random piper
        return self.clients[0]
