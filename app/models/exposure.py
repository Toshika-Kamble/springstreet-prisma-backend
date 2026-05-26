from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import utcnow

if TYPE_CHECKING:
    from app.models.fund import Fund


class SectorExposure(Base):
    __tablename__ = "sector_exposures"
    __table_args__ = (
        UniqueConstraint("fund_id", "sector", "as_of_date", name="uq_sector_exposure"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fund_id: Mapped[int] = mapped_column(
        ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sector: Mapped[str] = mapped_column(String(128), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    fund: Mapped["Fund"] = relationship("Fund", back_populates="sector_exposures")


class RegionExposure(Base):
    __tablename__ = "region_exposures"
    __table_args__ = (
        UniqueConstraint("fund_id", "region", "as_of_date", name="uq_region_exposure"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fund_id: Mapped[int] = mapped_column(
        ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    region: Mapped[str] = mapped_column(String(128), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    fund: Mapped["Fund"] = relationship("Fund", back_populates="region_exposures")


class MarketCapExposure(Base):
    __tablename__ = "market_cap_exposures"
    __table_args__ = (
        UniqueConstraint(
            "fund_id", "market_cap_bucket", "as_of_date", name="uq_market_cap_exposure"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fund_id: Mapped[int] = mapped_column(
        ForeignKey("funds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    market_cap_bucket: Mapped[str] = mapped_column(String(64), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    fund: Mapped["Fund"] = relationship("Fund", back_populates="market_cap_exposures")
