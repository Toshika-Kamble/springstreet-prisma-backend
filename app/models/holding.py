from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import utcnow

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.fund import Fund


class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (
        UniqueConstraint("fund_id", "asset_id", "as_of_date", name="uq_holding_fund_asset_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fund_id: Mapped[int] = mapped_column(
        ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    weight: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    shares: Mapped[Decimal | None] = mapped_column(Numeric(20, 4), nullable=True)
    market_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    fund: Mapped["Fund"] = relationship("Fund", back_populates="holdings")
    asset: Mapped["Asset"] = relationship("Asset", back_populates="holdings")
