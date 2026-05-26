from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.benchmark_repository import BenchmarkRepository
from app.repositories.exposure_repository import ExposureRepository
from app.repositories.fund_repository import FundRepository
from app.repositories.holding_repository import HoldingRepository
from app.repositories.performance_repository import PerformanceRepository
from app.repositories.price_repository import PriceRepository
from app.services.exposure_service import ExposureService
from app.services.fund_service import FundService
from app.services.performance_service import PerformanceService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_fund_repository(db: Session = Depends(get_db)) -> FundRepository:
    return FundRepository(db)


def get_holding_repository(db: Session = Depends(get_db)) -> HoldingRepository:
    return HoldingRepository(db)


def get_performance_repository(db: Session = Depends(get_db)) -> PerformanceRepository:
    return PerformanceRepository(db)


def get_exposure_repository(db: Session = Depends(get_db)) -> ExposureRepository:
    return ExposureRepository(db)


def get_price_repository(db: Session = Depends(get_db)) -> PriceRepository:
    return PriceRepository(db)


def get_benchmark_repository(db: Session = Depends(get_db)) -> BenchmarkRepository:
    return BenchmarkRepository(db)


def get_fund_service(
    fund_repo: FundRepository = Depends(get_fund_repository),
    holding_repo: HoldingRepository = Depends(get_holding_repository),
) -> FundService:
    return FundService(fund_repo, holding_repo)


def get_performance_service(
    fund_repo: FundRepository = Depends(get_fund_repository),
    performance_repo: PerformanceRepository = Depends(get_performance_repository),
    price_repo: PriceRepository = Depends(get_price_repository),
) -> PerformanceService:
    return PerformanceService(fund_repo, performance_repo, price_repo)


def get_exposure_service(
    fund_repo: FundRepository = Depends(get_fund_repository),
    exposure_repo: ExposureRepository = Depends(get_exposure_repository),
) -> ExposureService:
    return ExposureService(fund_repo, exposure_repo)
