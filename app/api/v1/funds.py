from fastapi import APIRouter, Depends, Path, Query

from app.core.dependencies import (
    get_exposure_service,
    get_fund_service,
    get_performance_service,
)
from app.schemas.common import FundFilterParams, PaginatedResponse, PaginationParams
from app.schemas.exposure import ExposureBreakdownResponse
from app.schemas.fund import FundListItem, FundResponse
from app.schemas.holding import HoldingResponse
from app.schemas.performance import FundPerformanceResponse
from app.services.exposure_service import ExposureService
from app.services.fund_service import FundService
from app.services.performance_service import PerformanceService

router = APIRouter()

FUND_ID_PATH = Path(
    ...,
    description="Fund ticker symbol (e.g. SPY, QQQ) or numeric id from GET /funds",
    examples=["SPY"],
)


@router.get("", response_model=PaginatedResponse[FundListItem])
def list_funds(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    fund_type: str | None = Query(None),
    is_active: bool | None = Query(None),
    search: str | None = Query(None, description="Search by name or ticker"),
    service: FundService = Depends(get_fund_service),
) -> PaginatedResponse[FundListItem]:
    return service.list_funds(
        PaginationParams(page=page, page_size=page_size),
        FundFilterParams(fund_type=fund_type, is_active=is_active, search=search),
    )


@router.get("/{identifier}", response_model=FundResponse)
def get_fund(
    identifier: str = FUND_ID_PATH,
    service: FundService = Depends(get_fund_service),
) -> FundResponse:
    return service.get_fund(identifier)


@router.get("/{identifier}/performance", response_model=FundPerformanceResponse)
def get_fund_performance(
    identifier: str = FUND_ID_PATH,
    snapshot_limit: int = Query(12, ge=1, le=60),
    service: PerformanceService = Depends(get_performance_service),
) -> FundPerformanceResponse:
    return service.get_performance(identifier, snapshot_limit=snapshot_limit)


@router.get("/{identifier}/holdings", response_model=PaginatedResponse[HoldingResponse])
def get_fund_holdings(
    identifier: str = FUND_ID_PATH,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: FundService = Depends(get_fund_service),
) -> PaginatedResponse[HoldingResponse]:
    return service.get_holdings(
        identifier,
        PaginationParams(page=page, page_size=page_size),
    )


@router.get("/{identifier}/exposure/regions", response_model=ExposureBreakdownResponse)
def get_region_exposure(
    identifier: str = FUND_ID_PATH,
    service: ExposureService = Depends(get_exposure_service),
) -> ExposureBreakdownResponse:
    return service.get_region_exposure(identifier)


@router.get("/{identifier}/exposure/sectors", response_model=ExposureBreakdownResponse)
def get_sector_exposure(
    identifier: str = FUND_ID_PATH,
    service: ExposureService = Depends(get_exposure_service),
) -> ExposureBreakdownResponse:
    return service.get_sector_exposure(identifier)


@router.get("/{identifier}/exposure/market-cap", response_model=ExposureBreakdownResponse)
def get_market_cap_exposure(
    identifier: str = FUND_ID_PATH,
    service: ExposureService = Depends(get_exposure_service),
) -> ExposureBreakdownResponse:
    return service.get_market_cap_exposure(identifier)
