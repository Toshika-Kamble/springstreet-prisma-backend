from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import utcnow

if TYPE_CHECKING:
    from app.models.benchmark import Benchmark
    from app.models.exposure import MarketCapExposure, RegionExposure, SectorExposure
    from app.models.holding import Holding
    from app.models.performance import FundPerformanceSnapshot
    from app.models.price import HistoricalPrice


class Fund(Base):
    __tablename__ = "funds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    fund_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    inception_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    aum: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    expense_ratio: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    benchmark_id: Mapped[int | None] = mapped_column(
        ForeignKey("benchmarks.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    benchmark: Mapped["Benchmark | None"] = relationship("Benchmark", back_populates="funds")
    holdings: Mapped[list["Holding"]] = relationship(
        "Holding", back_populates="fund", cascade="all, delete-orphan"
    )
    historical_prices: Mapped[list["HistoricalPrice"]] = relationship(
        "HistoricalPrice",
        back_populates="fund",
        foreign_keys="HistoricalPrice.fund_id",
        cascade="all, delete-orphan",
    )
    performance_snapshots: Mapped[list["FundPerformanceSnapshot"]] = relationship(
        "FundPerformanceSnapshot",
        back_populates="fund",
        cascade="all, delete-orphan",
    )
    sector_exposures: Mapped[list["SectorExposure"]] = relationship(
        "SectorExposure", back_populates="fund", cascade="all, delete-orphan"
    )
    region_exposures: Mapped[list["RegionExposure"]] = relationship(
        "RegionExposure", back_populates="fund", cascade="all, delete-orphan"
    )
    market_cap_exposures: Mapped[list["MarketCapExposure"]] = relationship(
        "MarketCapExposure", back_populates="fund", cascade="all, delete-orphan"
    )
