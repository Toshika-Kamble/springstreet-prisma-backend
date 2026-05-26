from app.core.exceptions import NotFoundError
from app.repositories.fund_repository import FundRepository
from app.repositories.holding_repository import HoldingRepository
from app.schemas.common import FundFilterParams, PaginatedResponse, PaginationParams
from app.schemas.fund import FundListItem, FundResponse
from app.schemas.holding import HoldingResponse


class FundService:
    def __init__(
        self,
        fund_repo: FundRepository,
        holding_repo: HoldingRepository,
    ) -> None:
        self.fund_repo = fund_repo
        self.holding_repo = holding_repo

    def _require_fund(self, identifier: str):
        fund = self.fund_repo.get_by_identifier(identifier)
        if not fund:
            raise NotFoundError(
                "Fund",
                identifier,
                hint="Use the ticker symbol from the list (e.g. SPY), not the numeric id or benchmark_ticker.",
            )
        return fund

    def list_funds(
        self,
        pagination: PaginationParams,
        filters: FundFilterParams,
    ) -> PaginatedResponse[FundListItem]:
        offset = (pagination.page - 1) * pagination.page_size
        funds, total = self.fund_repo.list_funds(filters, offset, pagination.page_size)
        items = [
            FundListItem(
                id=f.id,
                ticker=f.ticker,
                name=f.name,
                fund_type=f.fund_type,
                currency=f.currency,
                is_active=f.is_active,
                benchmark_ticker=f.benchmark.ticker if f.benchmark else None,
            )
            for f in funds
        ]
        return PaginatedResponse.create(items, total, pagination.page, pagination.page_size)

    def get_fund(self, identifier: str) -> FundResponse:
        fund = self._require_fund(identifier)
        return FundResponse.model_validate(fund)

    def get_holdings(
        self,
        identifier: str,
        pagination: PaginationParams,
    ) -> PaginatedResponse[HoldingResponse]:
        fund = self._require_fund(identifier)
        offset = (pagination.page - 1) * pagination.page_size
        holdings, total, _ = self.holding_repo.list_by_fund(
            fund.id, offset=offset, limit=pagination.page_size
        )
        items = [HoldingResponse.model_validate(h) for h in holdings]
        return PaginatedResponse.create(items, total, pagination.page, pagination.page_size)
