from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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


class PricePoint(BaseModel):
    date: date
    close: Decimal
    adj_close: Decimal | None = None


class FundPerformanceResponse(BaseModel):
    ticker: str
    latest_snapshot: PerformanceSnapshotResponse | None
    historical_snapshots: list[PerformanceSnapshotResponse] = []
    price_history: list[PricePoint] = []
