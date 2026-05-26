from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ExposureItem(BaseModel):
    label: str
    weight: Decimal = Field(..., description="Exposure weight as decimal")
    as_of_date: date

    @field_serializer("weight")
    def serialize_weight(self, value: Decimal) -> float:
        return float(value)


class ExposureBreakdownResponse(BaseModel):
    ticker: str
    as_of_date: date | None
    exposures: list[ExposureItem]
    total_weight: Decimal

    @field_serializer("total_weight")
    def serialize_total(self, value: Decimal) -> float:
        return float(value)
