from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.performance import FundPerformanceSnapshot


class PerformanceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest(self, fund_id: int) -> FundPerformanceSnapshot | None:
        stmt = (
            select(FundPerformanceSnapshot)
            .where(FundPerformanceSnapshot.fund_id == fund_id)
            .order_by(FundPerformanceSnapshot.as_of_date.desc())
            .limit(1)
        )
        return self.db.scalars(stmt).first()

    def list_snapshots(
        self,
        fund_id: int,
        limit: int = 30,
    ) -> list[FundPerformanceSnapshot]:
        stmt = (
            select(FundPerformanceSnapshot)
            .where(FundPerformanceSnapshot.fund_id == fund_id)
            .order_by(FundPerformanceSnapshot.as_of_date.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def upsert_snapshot(self, snapshot: FundPerformanceSnapshot) -> FundPerformanceSnapshot:
        stmt = select(FundPerformanceSnapshot).where(
            FundPerformanceSnapshot.fund_id == snapshot.fund_id,
            FundPerformanceSnapshot.as_of_date == snapshot.as_of_date,
        )
        existing = self.db.scalars(stmt).first()
        if existing:
            for attr in (
                "cagr",
                "volatility",
                "sharpe_ratio",
                "max_drawdown",
                "total_return",
                "ytd_return",
                "one_year_return",
                "three_year_return",
                "five_year_return",
            ):
                setattr(existing, attr, getattr(snapshot, attr))
            self.db.flush()
            return existing
        self.db.add(snapshot)
        self.db.flush()
        return snapshot
