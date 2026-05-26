from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BenchmarkSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    name: str


class FundBase(BaseModel):
    ticker: str
    name: str
    description: str | None = None
    fund_type: str | None = None
    inception_date: date | None = None
    currency: str = "USD"
    aum: Decimal | None = None
    expense_ratio: Decimal | None = None
    is_active: bool = True


class FundResponse(FundBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    benchmark: BenchmarkSummary | None = None
    created_at: datetime
    updated_at: datetime


class FundListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    name: str
    fund_type: str | None
    currency: str
    is_active: bool
    benchmark_ticker: str | None = None
