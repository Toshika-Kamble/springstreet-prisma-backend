from fastapi import APIRouter, Depends, Query

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


@router.get("/{ticker}", response_model=FundResponse)
def get_fund(
    ticker: str,
    service: FundService = Depends(get_fund_service),
) -> FundResponse:
    return service.get_fund(ticker)


@router.get("/{ticker}/performance", response_model=FundPerformanceResponse)
def get_fund_performance(
    ticker: str,
    snapshot_limit: int = Query(12, ge=1, le=60),
    service: PerformanceService = Depends(get_performance_service),
) -> FundPerformanceResponse:
    return service.get_performance(ticker, snapshot_limit=snapshot_limit)


@router.get("/{ticker}/holdings", response_model=PaginatedResponse[HoldingResponse])
def get_fund_holdings(
    ticker: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: FundService = Depends(get_fund_service),
) -> PaginatedResponse[HoldingResponse]:
    return service.get_holdings(
        ticker,
        PaginationParams(page=page, page_size=page_size),
    )


@router.get("/{ticker}/exposure/regions", response_model=ExposureBreakdownResponse)
def get_region_exposure(
    ticker: str,
    service: ExposureService = Depends(get_exposure_service),
) -> ExposureBreakdownResponse:
    return service.get_region_exposure(ticker)


@router.get("/{ticker}/exposure/sectors", response_model=ExposureBreakdownResponse)
def get_sector_exposure(
    ticker: str,
    service: ExposureService = Depends(get_exposure_service),
) -> ExposureBreakdownResponse:
    return service.get_sector_exposure(ticker)


@router.get("/{ticker}/exposure/market-cap", response_model=ExposureBreakdownResponse)
def get_market_cap_exposure(
    ticker: str,
    service: ExposureService = Depends(get_exposure_service),
) -> ExposureBreakdownResponse:
    return service.get_market_cap_exposure(ticker)
