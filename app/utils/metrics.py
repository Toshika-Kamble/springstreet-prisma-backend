"""Financial metrics computed from price series."""

from datetime import date

import numpy as np
import pandas as pd


def prices_to_returns(prices: pd.Series) -> pd.Series:
    return prices.pct_change().dropna()


def compute_cagr(prices: pd.Series) -> float | None:
    if prices.empty or len(prices) < 2:
        return None
    start = float(prices.iloc[0])
    end = float(prices.iloc[-1])
    if start <= 0:
        return None
    days = (prices.index[-1] - prices.index[0]).days
    if days <= 0:
        return None
    years = days / 365.25
    return (end / start) ** (1 / years) - 1


def compute_volatility(returns: pd.Series, periods_per_year: int = 252) -> float | None:
    if returns.empty or len(returns) < 2:
        return None
    return float(returns.std() * np.sqrt(periods_per_year))


def compute_sharpe(
    returns: pd.Series,
    risk_free_rate: float = 0.04,
    periods_per_year: int = 252,
) -> float | None:
    vol = compute_volatility(returns, periods_per_year)
    if vol is None or vol == 0:
        return None
    excess = returns.mean() * periods_per_year - risk_free_rate
    return float(excess / vol)


def compute_max_drawdown(prices: pd.Series) -> float | None:
    if prices.empty:
        return None
    cumulative = prices / prices.cummax()
    drawdown = cumulative - 1
    return float(drawdown.min())


def compute_period_return(prices: pd.Series, start: date, end: date | None = None) -> float | None:
    if prices.empty:
        return None
    end = end or prices.index[-1].date() if hasattr(prices.index[-1], "date") else prices.index[-1]
    if isinstance(end, pd.Timestamp):
        end = end.date()
    if isinstance(start, pd.Timestamp):
        start = start.date()

    mask = (prices.index >= pd.Timestamp(start)) & (prices.index <= pd.Timestamp(end))
    subset = prices.loc[mask]
    if len(subset) < 2:
        return None
    start_price = float(subset.iloc[0])
    end_price = float(subset.iloc[-1])
    if start_price <= 0:
        return None
    return end_price / start_price - 1


def compute_ytd_return(prices: pd.Series, as_of: date | None = None) -> float | None:
    if prices.empty:
        return None
    last = prices.index[-1]
    if isinstance(last, pd.Timestamp):
        ref = as_of or last.date()
    else:
        ref = as_of or last
    year_start = date(ref.year, 1, 1)
    return compute_period_return(prices, year_start, ref)


def compute_all_metrics(
    prices: pd.Series,
    risk_free_rate: float = 0.04,
) -> dict[str, float | None]:
    returns = prices_to_returns(prices)
    total_return = None
    if len(prices) >= 2 and float(prices.iloc[0]) > 0:
        total_return = float(prices.iloc[-1] / prices.iloc[0] - 1)

    one_year_ago = prices.index[-1] - pd.Timedelta(days=365)
    three_years_ago = prices.index[-1] - pd.Timedelta(days=365 * 3)
    five_years_ago = prices.index[-1] - pd.Timedelta(days=365 * 5)

    return {
        "cagr": compute_cagr(prices),
        "volatility": compute_volatility(returns),
        "sharpe_ratio": compute_sharpe(returns, risk_free_rate),
        "max_drawdown": compute_max_drawdown(prices),
        "total_return": total_return,
        "ytd_return": compute_ytd_return(prices),
        "one_year_return": compute_period_return(prices, one_year_ago.date())
        if hasattr(one_year_ago, "date")
        else compute_period_return(prices, one_year_ago),
        "three_year_return": compute_period_return(prices, three_years_ago.date())
        if len(prices.loc[prices.index >= three_years_ago]) >= 2
        else None,
        "five_year_return": compute_period_return(prices, five_years_ago.date())
        if len(prices.loc[prices.index >= five_years_ago]) >= 2
        else None,
    }
