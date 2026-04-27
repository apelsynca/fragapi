import json

from src.exceptions import ResourceNotFound


class GiftService:
    def __init__(self) -> None:
        with open("gift-models.json") as f:
            self.data: dict[str, list[str]] = json.load(f)

    async def get_models_by_shortname(self, shortname: str) -> list[str]:
        try:
            return self.data[shortname]
        except KeyError:
            raise ResourceNotFound(f"Gift with shortname '{shortname}' not found")


gift = GiftService()
