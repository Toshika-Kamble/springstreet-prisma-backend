from datetime import date
from decimal import Decimal

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.exposure import MarketCapExposure, RegionExposure, SectorExposure


class ExposureRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _latest_date(self, model: type, fund_id: int) -> date | None:
        stmt = select(func.max(model.as_of_date)).where(model.fund_id == fund_id)
        return self.db.scalar(stmt)

    def list_sector_exposures(
        self, fund_id: int, as_of_date: date | None = None
    ) -> tuple[list[SectorExposure], date | None]:
        latest = as_of_date or self._latest_date(SectorExposure, fund_id)
        if not latest:
            return [], None
        stmt = select(SectorExposure).where(
            SectorExposure.fund_id == fund_id, SectorExposure.as_of_date == latest
        )
        return list(self.db.scalars(stmt).all()), latest

    def list_region_exposures(
        self, fund_id: int, as_of_date: date | None = None
    ) -> tuple[list[RegionExposure], date | None]:
        latest = as_of_date or self._latest_date(RegionExposure, fund_id)
        if not latest:
            return [], None
        stmt = select(RegionExposure).where(
            RegionExposure.fund_id == fund_id, RegionExposure.as_of_date == latest
        )
        return list(self.db.scalars(stmt).all()), latest

    def list_market_cap_exposures(
        self, fund_id: int, as_of_date: date | None = None
    ) -> tuple[list[MarketCapExposure], date | None]:
        latest = as_of_date or self._latest_date(MarketCapExposure, fund_id)
        if not latest:
            return [], None
        stmt = select(MarketCapExposure).where(
            MarketCapExposure.fund_id == fund_id,
            MarketCapExposure.as_of_date == latest,
        )
        return list(self.db.scalars(stmt).all()), latest

    def replace_sector_exposures(
        self, fund_id: int, as_of_date: date, rows: list[tuple[str, Decimal]]
    ) -> None:
        self.db.execute(
            delete(SectorExposure).where(
                SectorExposure.fund_id == fund_id,
                SectorExposure.as_of_date == as_of_date,
            )
        )
        for sector, weight in rows:
            self.db.add(
                SectorExposure(fund_id=fund_id, sector=sector, weight=weight, as_of_date=as_of_date)
            )
        self.db.flush()

    def replace_region_exposures(
        self, fund_id: int, as_of_date: date, rows: list[tuple[str, Decimal]]
    ) -> None:
        self.db.execute(
            delete(RegionExposure).where(
                RegionExposure.fund_id == fund_id,
                RegionExposure.as_of_date == as_of_date,
            )
        )
        for region, weight in rows:
            self.db.add(
                RegionExposure(fund_id=fund_id, region=region, weight=weight, as_of_date=as_of_date)
            )
        self.db.flush()

    def replace_market_cap_exposures(
        self, fund_id: int, as_of_date: date, rows: list[tuple[str, Decimal]]
    ) -> None:
        self.db.execute(
            delete(MarketCapExposure).where(
                MarketCapExposure.fund_id == fund_id,
                MarketCapExposure.as_of_date == as_of_date,
            )
        )
        for bucket, weight in rows:
            self.db.add(
                MarketCapExposure(
                    fund_id=fund_id,
                    market_cap_bucket=bucket,
                    weight=weight,
                    as_of_date=as_of_date,
                )
            )
        self.db.flush()
