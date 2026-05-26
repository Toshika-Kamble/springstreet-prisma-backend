from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class AssetSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    name: str
    sector: str | None
    region: str | None
    market_cap_bucket: str | None


class HoldingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    weight: Decimal = Field(..., description="Portfolio weight as decimal (e.g. 0.05 = 5%)")
    shares: Decimal | None
    market_value: Decimal | None
    as_of_date: date
    asset: AssetSummary

    @field_serializer("weight", "shares", "market_value")
    def serialize_decimal(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None
