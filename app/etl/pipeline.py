"""Daily ETL orchestration."""

import logging
from datetime import date

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.etl.analytics import build_performance_snapshot
from app.etl.exposure import aggregate_exposures
from app.etl.market_data import dataframe_to_price_rows, fetch_historical_prices
from app.repositories.exposure_repository import ExposureRepository
from app.repositories.fund_repository import FundRepository
from app.repositories.holding_repository import HoldingRepository
from app.repositories.performance_repository import PerformanceRepository
from app.repositories.price_repository import PriceRepository

logger = logging.getLogger(__name__)


class DailyETLPipeline:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.fund_repo = FundRepository(db)
        self.price_repo = PriceRepository(db)
        self.performance_repo = PerformanceRepository(db)
        self.holding_repo = HoldingRepository(db)
        self.exposure_repo = ExposureRepository(db)
        self.settings = get_settings()

    def run(self) -> dict[str, int]:
        stats = {"funds_processed": 0, "prices_upserted": 0, "snapshots_updated": 0}
        tickers = self.fund_repo.list_active_tickers()
        logger.info("Starting daily ETL for %d funds", len(tickers))

        for ticker in tickers:
            try:
                fund = self.fund_repo.get_by_ticker(ticker)
                if not fund:
                    continue
                count = self._sync_fund_prices(fund.id, fund.ticker)
                stats["prices_upserted"] += count
                self._sync_performance(fund.id)
                stats["snapshots_updated"] += 1
                self._sync_exposures(fund.id)
                stats["funds_processed"] += 1
            except Exception:
                logger.exception("ETL failed for fund %s", ticker)
                self.db.rollback()
                continue

        self.db.commit()
        logger.info("Daily ETL complete: %s", stats)
        return stats

    def _sync_fund_prices(self, fund_id: int, ticker: str) -> int:
        df = fetch_historical_prices(ticker, self.settings.yfinance_lookback_years)
        if df.empty:
            return 0
        rows = dataframe_to_price_rows(df, ticker, fund_id=fund_id)
        return self.price_repo.bulk_upsert_prices(rows)

    def _sync_performance(self, fund_id: int) -> None:
        prices = self.price_repo.get_price_series_for_fund(fund_id)
        snapshot = build_performance_snapshot(fund_id, prices, as_of=date.today())
        if snapshot:
            self.performance_repo.upsert_snapshot(snapshot)

    def _sync_exposures(self, fund_id: int) -> None:
        holdings, _, as_of = self.holding_repo.list_by_fund(fund_id, limit=500)
        if not as_of or not holdings:
            return
        aggregated = aggregate_exposures(holdings)
        self.exposure_repo.replace_sector_exposures(fund_id, as_of, aggregated["sector"])
        self.exposure_repo.replace_region_exposures(fund_id, as_of, aggregated["region"])
        self.exposure_repo.replace_market_cap_exposures(fund_id, as_of, aggregated["market_cap"])
