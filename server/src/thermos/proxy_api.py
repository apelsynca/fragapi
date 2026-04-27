from httpx import AsyncClient

from src.thermos.types import GetCollectionResponse, GiftCollection, ThermosGiftModel


class ThermosError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.status_code = status_code
        self.message = message

        super().__init__(f"{message} [{status_code}]")


class ThermosProxyAPI:
    BASE_URL: str = "https://proxy.thermos.gifts/api/v1"

    def __init__(self, base_url: str = BASE_URL) -> None:
        self.base_url = base_url

        self.client = AsyncClient(
            headers={
                "Content-Type": "application/json",
            },
            base_url=base_url,
        )

    async def get_collections(self) -> list[GiftCollection]:
        response = await self.client.get(url="/collections")

        if response.status_code != 200:
            raise ThermosError(
                "Error getting collections", status_code=response.status_code
            )

        json = response.json()

        return [GiftCollection.model_validate(obj) for obj in json]

    async def get_collection(self, collection_name: str) -> GetCollectionResponse:
        response = await self.client.get(url=f"/collections/{collection_name}")

        if response.status_code != 200:
            raise ThermosError(
                "Error getting collection", status_code=response.status_code
            )

        json = response.json()

        return GetCollectionResponse.model_validate(json)

    async def get_collection_model(
        self, collection_name: str, model_name: str
    ) -> ThermosGiftModel:
        response = await self.client.get(
            url=f"/collections/{collection_name}/models/{model_name}"
        )

        if response.status_code != 200:
            raise ThermosError(
                "Error getting collection model name", status_code=response.status_code
            )

        json = response.json()

        return ThermosGiftModel.model_validate(json)
