from pydantic import BaseModel, Field, field_validator


class AggregatedStats(BaseModel):
    count: int = Field(ge=0)
    floor: float

    @field_validator("floor", mode="before")
    @classmethod
    def convert_nano_to_ton(cls, value: str) -> float:
        return int(value) / 1_000_000_000


class GiftCollection(BaseModel):
    name: str
    image_url: str
    stats: AggregatedStats
    id: str

    @property
    def short_name(self) -> str:
        return (
            self.name.strip().lower().replace(" ", "").replace("'", "").replace("-", "")
        )


class ThermosGiftModel(BaseModel):
    name: str
    rarity_per_mille: int
    image_url: str
    stats: AggregatedStats


class GiftCollectionAttributes(BaseModel):
    models: list[ThermosGiftModel]
    backdrops: list
    symbols: list


class GetCollectionResponse(BaseModel):
    collection: GiftCollection
    attributes: GiftCollectionAttributes
