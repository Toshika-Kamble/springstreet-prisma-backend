"""Compute performance analytics from price series."""

import logging
from datetime import date
from decimal import Decimal

import pandas as pd

from app.core.config import get_settings
from app.models.performance import FundPerformanceSnapshot
from app.utils.metrics import compute_all_metrics

logger = logging.getLogger(__name__)


def prices_to_dataframe(prices: list) -> pd.Series:
    data = {p.price_date: float(p.adj_close or p.close) for p in prices}
    series = pd.Series(data)
    series.index = pd.to_datetime(series.index)
    return series.sort_index()


def build_performance_snapshot(fund_id: int, prices: list, as_of: date | None = None) -> FundPerformanceSnapshot | None:
    if len(prices) < 2:
        logger.warning("Insufficient prices for fund_id=%s", fund_id)
        return None

    settings = get_settings()
    series = prices_to_dataframe(prices)
    metrics = compute_all_metrics(series, risk_free_rate=settings.risk_free_rate)
    as_of_date = as_of or series.index[-1].date()

    def to_decimal(val: float | None) -> Decimal | None:
        if val is None:
            return None
        return Decimal(str(round(val, 6)))

    return FundPerformanceSnapshot(
        fund_id=fund_id,
        as_of_date=as_of_date,
        cagr=to_decimal(metrics["cagr"]),
        volatility=to_decimal(metrics["volatility"]),
        sharpe_ratio=to_decimal(metrics["sharpe_ratio"]),
        max_drawdown=to_decimal(metrics["max_drawdown"]),
        total_return=to_decimal(metrics["total_return"]),
        ytd_return=to_decimal(metrics["ytd_return"]),
        one_year_return=to_decimal(metrics["one_year_return"]),
        three_year_return=to_decimal(metrics["three_year_return"]),
        five_year_return=to_decimal(metrics["five_year_return"]),
    )
