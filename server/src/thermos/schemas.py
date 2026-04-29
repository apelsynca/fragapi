from src.kit.schemas import Schema


class GiftModel(Schema):
    name: str
    floor: float
    count: int
    image_url: str
