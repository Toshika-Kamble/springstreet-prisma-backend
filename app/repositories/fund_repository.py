from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.fund import Fund
from app.schemas.common import FundFilterParams


class FundRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_ticker(self, ticker: str) -> Fund | None:
        stmt = (
            select(Fund)
            .options(joinedload(Fund.benchmark))
            .where(func.upper(Fund.ticker) == ticker.upper())
        )
        return self.db.scalars(stmt).unique().first()

    def get_by_id(self, fund_id: int) -> Fund | None:
        stmt = (
            select(Fund)
            .options(joinedload(Fund.benchmark))
            .where(Fund.id == fund_id)
        )
        return self.db.scalars(stmt).unique().first()

    def list_funds(
        self,
        filters: FundFilterParams,
        offset: int,
        limit: int,
    ) -> tuple[list[Fund], int]:
        stmt = select(Fund).options(joinedload(Fund.benchmark))
        count_stmt = select(func.count()).select_from(Fund)

        if filters.is_active is not None:
            stmt = stmt.where(Fund.is_active == filters.is_active)
            count_stmt = count_stmt.where(Fund.is_active == filters.is_active)
        if filters.fund_type:
            stmt = stmt.where(Fund.fund_type == filters.fund_type)
            count_stmt = count_stmt.where(Fund.fund_type == filters.fund_type)
        if filters.search:
            # func.lower + like works on SQLite and PostgreSQL (ilike is PG-oriented)
            term = f"%{filters.search.strip().lower()}%"
            condition = or_(
                func.lower(Fund.name).like(term),
                func.lower(Fund.ticker).like(term),
            )
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        total = self.db.scalar(count_stmt) or 0
        stmt = stmt.order_by(Fund.ticker).offset(offset).limit(limit)
        items = list(self.db.scalars(stmt).unique().all())
        return items, total

    def list_active_tickers(self) -> list[str]:
        stmt = select(Fund.ticker).where(Fund.is_active.is_(True))
        return list(self.db.scalars(stmt).all())

    def upsert_fund(self, fund: Fund) -> Fund:
        existing = self.get_by_ticker(fund.ticker)
        if existing:
            for attr in (
                "name",
                "description",
                "fund_type",
                "inception_date",
                "currency",
                "aum",
                "expense_ratio",
                "benchmark_id",
                "is_active",
            ):
                val = getattr(fund, attr, None)
                if val is not None:
                    setattr(existing, attr, val)
            self.db.flush()
            return existing
        self.db.add(fund)
        self.db.flush()
        return fund
