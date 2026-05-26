from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class PerformanceSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    as_of_date: date
    cagr: Decimal | None = Field(None, description="Compound annual growth rate")
    volatility: Decimal | None = Field(None, description="Annualized volatility")
    sharpe_ratio: Decimal | None = None
    max_drawdown: Decimal | None = None
    total_return: Decimal | None = None
    ytd_return: Decimal | None = None
    one_year_return: Decimal | None = None
    three_year_return: Decimal | None = None
    five_year_return: Decimal | None = None

    @field_serializer(
        "cagr",
        "volatility",
        "sharpe_ratio",
        "max_drawdown",
        "total_return",
        "ytd_return",
        "one_year_return",
        "three_year_return",
        "five_year_return",
    )
    def serialize_metrics(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


class PricePoint(BaseModel):
    date: date
    close: Decimal
    adj_close: Decimal | None = None

    @field_serializer("close", "adj_close")
    def serialize_price(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


class FundPerformanceResponse(BaseModel):
    ticker: str
    latest_snapshot: PerformanceSnapshotResponse | None
    historical_snapshots: list[PerformanceSnapshotResponse] = []
    price_history: list[PricePoint] = []
