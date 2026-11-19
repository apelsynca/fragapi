from typing import Annotated

from pydantic import Field, field_validator

from src.kit.schemas import Schema

AttributionValue = Annotated[str, Field(max_length=128, pattern=r"^[^\x00-\x1f\x7f]*$")]


class Attribution(Schema):
    source: AttributionValue | None = None
    medium: AttributionValue | None = None
    campaign: AttributionValue | None = None
    referrer: (
        Annotated[str, Field(max_length=253, pattern=r"^[a-zA-Z0-9._:-]+$")] | None
    ) = None

    @field_validator("source", "medium", "campaign", "referrer", mode="before")
    @classmethod
    def normalize(cls, value: object) -> object:
        return (value.strip() or None) if isinstance(value, str) else value

    @property
    def is_empty(self) -> bool:
        return not any(self.model_dump().values())
