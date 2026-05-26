"""Fetch market data from yfinance."""

import logging
from datetime import date, timedelta

import pandas as pd
import yfinance as yf

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def fetch_historical_prices(
    symbol: str,
    lookback_years: int | None = None,
) -> pd.DataFrame:
    settings = get_settings()
    years = lookback_years or settings.yfinance_lookback_years
    start = date.today() - timedelta(days=365 * years)

    logger.info("Fetching prices for %s from %s", symbol, start)
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start.isoformat(), auto_adjust=False)

    if df.empty:
        logger.warning("No price data returned for %s", symbol)
        return df

    df = df.reset_index()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    return df


def dataframe_to_price_rows(
    df: pd.DataFrame,
    symbol: str,
    fund_id: int | None = None,
    asset_id: int | None = None,
) -> list[dict]:
    rows: list[dict] = []
    for _, row in df.iterrows():
        price_date = row["Date"].date() if hasattr(row["Date"], "date") else row["Date"]
        rows.append(
            {
                "symbol": symbol.upper(),
                "fund_id": fund_id,
                "asset_id": asset_id,
                "price_date": price_date,
                "open": _safe_decimal(row.get("Open")),
                "high": _safe_decimal(row.get("High")),
                "low": _safe_decimal(row.get("Low")),
                "close": _safe_decimal(row.get("Close")),
                "adj_close": _safe_decimal(row.get("Adj Close")),
                "volume": int(row["Volume"]) if pd.notna(row.get("Volume")) else None,
            }
        )
    return rows


def _safe_decimal(value) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return float(value)
