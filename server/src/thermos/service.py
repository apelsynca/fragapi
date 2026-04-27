from src.exceptions import ResourceNotFound
from src.thermos.proxy_api import ThermosProxyAPI
from src.thermos.schemas import GiftModel


def shortify(name: str) -> str:
    return (
        name.replace(" ", "").replace("-", "").replace("'", "").replace(".", "").lower()
    )


class ThermosService:
    def __init__(self) -> None:
        self.api = ThermosProxyAPI()

    async def find_collection_model(self, short_name: str, model: str) -> GiftModel:
        collections = await self.api.get_collections()

        try:
            collection = next(x for x in collections if shortify(x.name) == short_name)
        except StopIteration:
            raise ResourceNotFound("Collection not found")

        collection_data = await self.api.get_collection(collection_name=collection.name)

        try:
            collection_model = next(
                m
                for m in collection_data.attributes.models
                if shortify(m.name) == model
            )
        except StopIteration:
            raise ResourceNotFound("Model not found")

        return GiftModel(
            name=model,
            floor=collection_model.stats.floor,
            count=collection_model.stats.count,
        )


thermos = ThermosService()
