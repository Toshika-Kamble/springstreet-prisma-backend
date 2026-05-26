from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import utcnow

if TYPE_CHECKING:
    from app.models.fund import Fund


class FundPerformanceSnapshot(Base):
    __tablename__ = "fund_performance_snapshots"
    __table_args__ = (
        UniqueConstraint("fund_id", "as_of_date", name="uq_fund_performance_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fund_id: Mapped[int] = mapped_column(
        ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    cagr: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    volatility: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    sharpe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    max_drawdown: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    total_return: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    ytd_return: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    one_year_return: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    three_year_return: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    five_year_return: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    fund: Mapped["Fund"] = relationship("Fund", back_populates="performance_snapshots")
