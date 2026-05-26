from decimal import Decimal

from app.core.exceptions import NotFoundError
from app.repositories.exposure_repository import ExposureRepository
from app.repositories.fund_repository import FundRepository
from app.schemas.exposure import ExposureBreakdownResponse, ExposureItem


class ExposureService:
    def __init__(
        self,
        fund_repo: FundRepository,
        exposure_repo: ExposureRepository,
    ) -> None:
        self.fund_repo = fund_repo
        self.exposure_repo = exposure_repo

    def _require_fund(self, ticker: str):
        fund = self.fund_repo.get_by_ticker(ticker)
        if not fund:
            raise NotFoundError("Fund", ticker)
        return fund

    def _build_response(
        self,
        ticker: str,
        rows: list,
        label_attr: str,
        as_of_date,
    ) -> ExposureBreakdownResponse:
        exposures = [
            ExposureItem(
                label=getattr(r, label_attr),
                weight=r.weight,
                as_of_date=r.as_of_date,
            )
            for r in rows
        ]
        total = sum((r.weight for r in rows), Decimal("0"))
        return ExposureBreakdownResponse(
            ticker=ticker,
            as_of_date=as_of_date,
            exposures=exposures,
            total_weight=total,
        )

    def get_sector_exposure(self, ticker: str) -> ExposureBreakdownResponse:
        fund = self._require_fund(ticker)
        rows, as_of = self.exposure_repo.list_sector_exposures(fund.id)
        return self._build_response(ticker, rows, "sector", as_of)

    def get_region_exposure(self, ticker: str) -> ExposureBreakdownResponse:
        fund = self._require_fund(ticker)
        rows, as_of = self.exposure_repo.list_region_exposures(fund.id)
        return self._build_response(ticker, rows, "region", as_of)

    def get_market_cap_exposure(self, ticker: str) -> ExposureBreakdownResponse:
        fund = self._require_fund(ticker)
        rows, as_of = self.exposure_repo.list_market_cap_exposures(fund.id)
        return self._build_response(ticker, rows, "market_cap_bucket", as_of)
