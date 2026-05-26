from datetime import date

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.db.session import engine
from app.models.price import HistoricalPrice


class PriceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_fund_prices(
        self,
        fund_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 500,
    ) -> list[HistoricalPrice]:
        stmt = select(HistoricalPrice).where(HistoricalPrice.fund_id == fund_id)
        if start_date:
            stmt = stmt.where(HistoricalPrice.price_date >= start_date)
        if end_date:
            stmt = stmt.where(HistoricalPrice.price_date <= end_date)
        stmt = stmt.order_by(HistoricalPrice.price_date.desc()).limit(limit)
        rows = list(self.db.scalars(stmt).all())
        rows.reverse()
        return rows

    def bulk_upsert_prices(self, rows: list[dict]) -> int:
        if not rows:
            return 0

        update_cols = {
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "adj_close": "adj_close",
            "volume": "volume",
            "fund_id": "fund_id",
            "asset_id": "asset_id",
        }

        if engine.dialect.name == "postgresql":
            stmt = pg_insert(HistoricalPrice).values(rows)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_historical_price_symbol_date",
                set_={k: stmt.excluded[k] for k in update_cols},
            )
        else:
            stmt = sqlite_insert(HistoricalPrice).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=["symbol", "price_date"],
                set_={k: getattr(stmt.excluded, k) for k in update_cols},
            )

        self.db.execute(stmt)
        self.db.flush()
        return len(rows)

    def get_price_series_for_fund(self, fund_id: int) -> list[HistoricalPrice]:
        stmt = (
            select(HistoricalPrice)
            .where(HistoricalPrice.fund_id == fund_id)
            .order_by(HistoricalPrice.price_date.asc())
        )
        return list(self.db.scalars(stmt).all())
