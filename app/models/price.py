from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import utcnow

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.fund import Fund


class HistoricalPrice(Base):
    __tablename__ = "historical_prices"
    __table_args__ = (
        UniqueConstraint(
            "symbol", "price_date", name="uq_historical_price_symbol_date"
        ),
        Index("ix_historical_prices_fund_date", "fund_id", "price_date"),
        Index("ix_historical_prices_asset_date", "asset_id", "price_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    fund_id: Mapped[int | None] = mapped_column(
        ForeignKey("funds.id", ondelete="CASCADE"), nullable=True
    )
    asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=True
    )
    price_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    open: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    high: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    low: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    close: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    adj_close: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    volume: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    fund: Mapped["Fund | None"] = relationship(
        "Fund", back_populates="historical_prices", foreign_keys=[fund_id]
    )
    asset: Mapped["Asset | None"] = relationship(
        "Asset", back_populates="historical_prices", foreign_keys=[asset_id]
    )
