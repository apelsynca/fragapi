import json

from src.exceptions import ResourceNotFound


class GiftService:
    def __init__(self) -> None:
        with open("gift-models.json") as f:
            self.data: dict[str, list[str]] = json.load(f)

    async def get_all_gift_model_strings_by_shortname(
        self, short_name: str
    ) -> list[str]:
        """
        Returns all gift model names (in short_name format) 
        related to collection (by collection short name)\
        """
        try:
            return self.data[short_name]
        except KeyError:
            raise ResourceNotFound(f"Gift with shortname '{short_name}' not found")


gift = GiftService()
