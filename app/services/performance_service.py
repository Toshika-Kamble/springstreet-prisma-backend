from app.core.exceptions import NotFoundError
from app.repositories.fund_repository import FundRepository
from app.repositories.performance_repository import PerformanceRepository
from app.repositories.price_repository import PriceRepository
from app.schemas.performance import (
    FundPerformanceResponse,
    PerformanceSnapshotResponse,
    PricePoint,
)


class PerformanceService:
    def __init__(
        self,
        fund_repo: FundRepository,
        performance_repo: PerformanceRepository,
        price_repo: PriceRepository,
    ) -> None:
        self.fund_repo = fund_repo
        self.performance_repo = performance_repo
        self.price_repo = price_repo

    def get_performance(self, identifier: str, snapshot_limit: int = 12) -> FundPerformanceResponse:
        fund = self.fund_repo.get_by_identifier(identifier)
        if not fund:
            raise NotFoundError(
                "Fund",
                identifier,
                hint="Use ticker (e.g. SPY) or numeric id from GET /funds.",
            )

        latest = self.performance_repo.get_latest(fund.id)
        snapshots = self.performance_repo.list_snapshots(fund.id, limit=snapshot_limit)
        prices = self.price_repo.list_fund_prices(fund.id, limit=252)

        return FundPerformanceResponse(
            ticker=fund.ticker,
            latest_snapshot=PerformanceSnapshotResponse.model_validate(latest)
            if latest
            else None,
            historical_snapshots=[
                PerformanceSnapshotResponse.model_validate(s) for s in snapshots
            ],
            price_history=[
                PricePoint(
                    date=p.price_date,
                    close=p.close,
                    adj_close=p.adj_close,
                )
                for p in prices
            ],
        )
