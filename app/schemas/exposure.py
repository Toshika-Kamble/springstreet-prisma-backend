from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExposureItem(BaseModel):
    label: str
    weight: Decimal = Field(..., description="Exposure weight as decimal")
    as_of_date: date


class ExposureBreakdownResponse(BaseModel):
    ticker: str
    as_of_date: date | None
    exposures: list[ExposureItem]
    total_weight: Decimal
