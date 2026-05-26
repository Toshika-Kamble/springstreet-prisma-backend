"""Load sample funds, holdings, exposures; optionally run yfinance ETL."""

import logging
import os
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.etl.exposure import aggregate_exposures
from app.etl.pipeline import DailyETLPipeline
from app.models.asset import Asset
from app.models.benchmark import Benchmark
from app.models.fund import Fund
from app.models.holding import Holding
from app.repositories.asset_repository import AssetRepository
from app.repositories.benchmark_repository import BenchmarkRepository
from app.repositories.exposure_repository import ExposureRepository
from app.repositories.fund_repository import FundRepository
from app.repositories.holding_repository import HoldingRepository

setup_logging()
logger = logging.getLogger(__name__)

SAMPLE_BENCHMARKS = [
    {"ticker": "^GSPC", "name": "S&P 500 Index", "description": "US large-cap benchmark"},
    {"ticker": "^IXIC", "name": "NASDAQ Composite", "description": "US tech-heavy benchmark"},
]

SAMPLE_FUNDS = [
    {
        "ticker": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "description": "Tracks the S&P 500 index.",
        "fund_type": "ETF",
        "inception_date": date(1993, 1, 22),
        "currency": "USD",
        "expense_ratio": Decimal("0.0945"),
        "benchmark_ticker": "^GSPC",
    },
    {
        "ticker": "QQQ",
        "name": "Invesco QQQ Trust",
        "description": "Tracks the NASDAQ-100 Index.",
        "fund_type": "ETF",
        "inception_date": date(1999, 3, 10),
        "currency": "USD",
        "expense_ratio": Decimal("0.2000"),
        "benchmark_ticker": "^IXIC",
    },
    {
        "ticker": "VTI",
        "name": "Vanguard Total Stock Market ETF",
        "description": "Broad US equity market exposure.",
        "fund_type": "ETF",
        "inception_date": date(2001, 5, 24),
        "currency": "USD",
        "expense_ratio": Decimal("0.0300"),
        "benchmark_ticker": "^GSPC",
    },
]

SAMPLE_HOLDINGS = {
    "SPY": [
        ("AAPL", "Apple Inc.", "Technology", "North America", "Large Cap", Decimal("0.0700")),
        ("MSFT", "Microsoft Corporation", "Technology", "North America", "Large Cap", Decimal("0.0650")),
        ("NVDA", "NVIDIA Corporation", "Technology", "North America", "Large Cap", Decimal("0.0600")),
        ("AMZN", "Amazon.com Inc.", "Consumer Cyclical", "North America", "Large Cap", Decimal("0.0400")),
        ("GOOGL", "Alphabet Inc.", "Communication Services", "North America", "Large Cap", Decimal("0.0350")),
        ("META", "Meta Platforms Inc.", "Communication Services", "North America", "Large Cap", Decimal("0.0300")),
        ("BRK-B", "Berkshire Hathaway", "Financial Services", "North America", "Large Cap", Decimal("0.0280")),
        ("JPM", "JPMorgan Chase", "Financial Services", "North America", "Large Cap", Decimal("0.0250")),
    ],
    "QQQ": [
        ("AAPL", "Apple Inc.", "Technology", "North America", "Large Cap", Decimal("0.1100")),
        ("MSFT", "Microsoft Corporation", "Technology", "North America", "Large Cap", Decimal("0.1000")),
        ("NVDA", "NVIDIA Corporation", "Technology", "North America", "Large Cap", Decimal("0.0950")),
        ("AMZN", "Amazon.com Inc.", "Consumer Cyclical", "North America", "Large Cap", Decimal("0.0550")),
        ("META", "Meta Platforms Inc.", "Communication Services", "North America", "Large Cap", Decimal("0.0450")),
        ("GOOGL", "Alphabet Inc.", "Communication Services", "North America", "Large Cap", Decimal("0.0420")),
        ("TSLA", "Tesla Inc.", "Consumer Cyclical", "North America", "Large Cap", Decimal("0.0380")),
        ("AVGO", "Broadcom Inc.", "Technology", "North America", "Large Cap", Decimal("0.0320")),
    ],
    "VTI": [
        ("AAPL", "Apple Inc.", "Technology", "North America", "Large Cap", Decimal("0.0550")),
        ("MSFT", "Microsoft Corporation", "Technology", "North America", "Large Cap", Decimal("0.0520")),
        ("NVDA", "NVIDIA Corporation", "Technology", "North America", "Large Cap", Decimal("0.0480")),
        ("AMZN", "Amazon.com Inc.", "Consumer Cyclical", "North America", "Large Cap", Decimal("0.0300")),
        ("GOOGL", "Alphabet Inc.", "Communication Services", "North America", "Large Cap", Decimal("0.0280")),
        ("BRK-B", "Berkshire Hathaway", "Financial Services", "North America", "Large Cap", Decimal("0.0220")),
        ("JNJ", "Johnson & Johnson", "Healthcare", "North America", "Large Cap", Decimal("0.0180")),
        ("XOM", "Exxon Mobil", "Energy", "North America", "Large Cap", Decimal("0.0160")),
    ],
}


def _seed_exposures(db, fund_id: int, as_of: date) -> None:
    holding_repo = HoldingRepository(db)
    exposure_repo = ExposureRepository(db)
    holdings, _, _ = holding_repo.list_by_fund(fund_id, as_of_date=as_of, limit=500)
    if not holdings:
        return
    aggregated = aggregate_exposures(holdings)
    exposure_repo.replace_sector_exposures(fund_id, as_of, aggregated["sector"])
    exposure_repo.replace_region_exposures(fund_id, as_of, aggregated["region"])
    exposure_repo.replace_market_cap_exposures(fund_id, as_of, aggregated["market_cap"])


def seed(run_etl: bool | None = None) -> None:
    if run_etl is None:
        run_etl = os.getenv("RUN_ETL_ON_SEED", "false").lower() in ("1", "true", "yes")

    db = SessionLocal()
    try:
        bench_repo = BenchmarkRepository(db)
        fund_repo = FundRepository(db)
        asset_repo = AssetRepository(db)

        benchmark_map: dict[str, int] = {}
        for b in SAMPLE_BENCHMARKS:
            bench = bench_repo.upsert(
                Benchmark(ticker=b["ticker"], name=b["name"], description=b["description"])
            )
            benchmark_map[bench.ticker] = bench.id

        as_of = date.today()
        for raw in SAMPLE_FUNDS:
            f_data = dict(raw)
            bench_id = benchmark_map.get(f_data.pop("benchmark_ticker"))
            fund = fund_repo.upsert_fund(
                Fund(
                    ticker=f_data["ticker"],
                    name=f_data["name"],
                    description=f_data["description"],
                    fund_type=f_data["fund_type"],
                    inception_date=f_data["inception_date"],
                    currency=f_data["currency"],
                    expense_ratio=f_data["expense_ratio"],
                    benchmark_id=bench_id,
                    is_active=True,
                )
            )

            for symbol, name, sector, region, cap, weight in SAMPLE_HOLDINGS[fund.ticker]:
                asset = asset_repo.upsert(
                    Asset(
                        symbol=symbol,
                        name=name,
                        asset_type="Equity",
                        sector=sector,
                        region=region,
                        market_cap_bucket=cap,
                    )
                )
                exists = db.scalars(
                    select(Holding).where(
                        Holding.fund_id == fund.id,
                        Holding.asset_id == asset.id,
                        Holding.as_of_date == as_of,
                    )
                ).first()
                if not exists:
                    db.add(
                        Holding(
                            fund_id=fund.id,
                            asset_id=asset.id,
                            weight=weight,
                            as_of_date=as_of,
                        )
                    )

            db.flush()
            _seed_exposures(db, fund.id, as_of)

        db.commit()
        logger.info("Sample funds, holdings, and exposures seeded.")

        if run_etl:
            logger.info("Running yfinance ETL (requires internet, may take 1-2 min)...")
            stats = DailyETLPipeline(db).run()
            logger.info("ETL stats: %s", stats)
        else:
            logger.info(
                "Skipped market ETL. Run: python -m scripts.run_etl  (needs internet)"
            )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
