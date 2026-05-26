"""Aggregate exposure metrics from holdings."""

import logging
from collections import defaultdict
from datetime import date
from decimal import Decimal

from app.models.holding import Holding

logger = logging.getLogger(__name__)

UNKNOWN = "Unknown"


def aggregate_exposures(holdings: list[Holding]) -> dict[str, list[tuple[str, Decimal]]]:
    sector_weights: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    region_weights: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    cap_weights: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

    for h in holdings:
        asset = h.asset
        sector = asset.sector or UNKNOWN
        region = asset.region or UNKNOWN
        cap = asset.market_cap_bucket or UNKNOWN
        sector_weights[sector] += h.weight
        region_weights[region] += h.weight
        cap_weights[cap] += h.weight

    def sorted_rows(weights: dict[str, Decimal]) -> list[tuple[str, Decimal]]:
        return sorted(weights.items(), key=lambda x: x[1], reverse=True)

    return {
        "sector": sorted_rows(sector_weights),
        "region": sorted_rows(region_weights),
        "market_cap": sorted_rows(cap_weights),
    }


def aggregate_exposures_for_date(
    holdings: list[Holding],
    as_of_date: date,
) -> dict[str, list[tuple[str, Decimal]]]:
    filtered = [h for h in holdings if h.as_of_date == as_of_date]
    if not filtered:
        filtered = holdings
    return aggregate_exposures(filtered)
