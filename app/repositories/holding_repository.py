from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.holding import Holding


class HoldingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_fund(
        self,
        fund_id: int,
        as_of_date: date | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[Holding], int, date | None]:
        latest_date = as_of_date or self._latest_as_of_date(fund_id)
        if latest_date is None:
            return [], 0, None

        base = (
            select(Holding)
            .options(joinedload(Holding.asset))
            .where(Holding.fund_id == fund_id, Holding.as_of_date == latest_date)
        )
        count_stmt = (
            select(func.count())
            .select_from(Holding)
            .where(Holding.fund_id == fund_id, Holding.as_of_date == latest_date)
        )
        total = self.db.scalar(count_stmt) or 0
        items = list(
            self.db.scalars(
                base.order_by(Holding.weight.desc()).offset(offset).limit(limit)
            ).all()
        )
        return items, total, latest_date

    def _latest_as_of_date(self, fund_id: int) -> date | None:
        stmt = select(func.max(Holding.as_of_date)).where(Holding.fund_id == fund_id)
        return self.db.scalar(stmt)

    def get_holdings_for_exposure(self, fund_id: int, as_of_date: date) -> list[Holding]:
        stmt = (
            select(Holding)
            .options(joinedload(Holding.asset))
            .where(Holding.fund_id == fund_id, Holding.as_of_date == as_of_date)
        )
        return list(self.db.scalars(stmt).all())
