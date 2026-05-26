"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-26

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "benchmarks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker"),
    )
    op.create_index("ix_benchmarks_ticker", "benchmarks", ["ticker"])

    op.create_table(
        "funds",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("fund_type", sa.String(length=64), nullable=True),
        sa.Column("inception_date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("aum", sa.Numeric(20, 2), nullable=True),
        sa.Column("expense_ratio", sa.Numeric(8, 4), nullable=True),
        sa.Column("benchmark_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["benchmark_id"], ["benchmarks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker"),
    )
    op.create_index("ix_funds_ticker", "funds", ["ticker"])

    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("asset_type", sa.String(length=64), nullable=True),
        sa.Column("sector", sa.String(length=128), nullable=True),
        sa.Column("region", sa.String(length=128), nullable=True),
        sa.Column("market_cap_bucket", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol"),
    )
    op.create_index("ix_assets_symbol", "assets", ["symbol"])
    op.create_index("ix_assets_sector", "assets", ["sector"])
    op.create_index("ix_assets_region", "assets", ["region"])
    op.create_index("ix_assets_market_cap_bucket", "assets", ["market_cap_bucket"])

    op.create_table(
        "holdings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Numeric(8, 6), nullable=False),
        sa.Column("shares", sa.Numeric(20, 4), nullable=True),
        sa.Column("market_value", sa.Numeric(20, 2), nullable=True),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["fund_id"], ["funds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fund_id", "asset_id", "as_of_date", name="uq_holding_fund_asset_date"),
    )
    op.create_index("ix_holdings_fund_id", "holdings", ["fund_id"])
    op.create_index("ix_holdings_asset_id", "holdings", ["asset_id"])
    op.create_index("ix_holdings_as_of_date", "holdings", ["as_of_date"])

    op.create_table(
        "historical_prices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=True),
        sa.Column("asset_id", sa.Integer(), nullable=True),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Numeric(18, 6), nullable=True),
        sa.Column("high", sa.Numeric(18, 6), nullable=True),
        sa.Column("low", sa.Numeric(18, 6), nullable=True),
        sa.Column("close", sa.Numeric(18, 6), nullable=False),
        sa.Column("adj_close", sa.Numeric(18, 6), nullable=True),
        sa.Column("volume", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["fund_id"], ["funds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol", "price_date", name="uq_historical_price_symbol_date"),
    )
    op.create_index("ix_historical_prices_symbol", "historical_prices", ["symbol"])
    op.create_index("ix_historical_prices_price_date", "historical_prices", ["price_date"])
    op.create_index("ix_historical_prices_fund_date", "historical_prices", ["fund_id", "price_date"])
    op.create_index("ix_historical_prices_asset_date", "historical_prices", ["asset_id", "price_date"])

    op.create_table(
        "fund_performance_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("cagr", sa.Numeric(12, 6), nullable=True),
        sa.Column("volatility", sa.Numeric(12, 6), nullable=True),
        sa.Column("sharpe_ratio", sa.Numeric(12, 6), nullable=True),
        sa.Column("max_drawdown", sa.Numeric(12, 6), nullable=True),
        sa.Column("total_return", sa.Numeric(12, 6), nullable=True),
        sa.Column("ytd_return", sa.Numeric(12, 6), nullable=True),
        sa.Column("one_year_return", sa.Numeric(12, 6), nullable=True),
        sa.Column("three_year_return", sa.Numeric(12, 6), nullable=True),
        sa.Column("five_year_return", sa.Numeric(12, 6), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["fund_id"], ["funds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fund_id", "as_of_date", name="uq_fund_performance_date"),
    )
    op.create_index("ix_fund_performance_snapshots_fund_id", "fund_performance_snapshots", ["fund_id"])
    op.create_index("ix_fund_performance_snapshots_as_of_date", "fund_performance_snapshots", ["as_of_date"])

    op.create_table(
        "sector_exposures",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=False),
        sa.Column("sector", sa.String(length=128), nullable=False),
        sa.Column("weight", sa.Numeric(8, 6), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["fund_id"], ["funds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fund_id", "sector", "as_of_date", name="uq_sector_exposure"),
    )
    op.create_index("ix_sector_exposures_fund_id", "sector_exposures", ["fund_id"])
    op.create_index("ix_sector_exposures_as_of_date", "sector_exposures", ["as_of_date"])

    op.create_table(
        "region_exposures",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=False),
        sa.Column("region", sa.String(length=128), nullable=False),
        sa.Column("weight", sa.Numeric(8, 6), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["fund_id"], ["funds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fund_id", "region", "as_of_date", name="uq_region_exposure"),
    )
    op.create_index("ix_region_exposures_fund_id", "region_exposures", ["fund_id"])
    op.create_index("ix_region_exposures_as_of_date", "region_exposures", ["as_of_date"])

    op.create_table(
        "market_cap_exposures",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("fund_id", sa.Integer(), nullable=False),
        sa.Column("market_cap_bucket", sa.String(length=64), nullable=False),
        sa.Column("weight", sa.Numeric(8, 6), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["fund_id"], ["funds.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fund_id", "market_cap_bucket", "as_of_date", name="uq_market_cap_exposure"),
    )
    op.create_index("ix_market_cap_exposures_fund_id", "market_cap_exposures", ["fund_id"])
    op.create_index("ix_market_cap_exposures_as_of_date", "market_cap_exposures", ["as_of_date"])


def downgrade() -> None:
    op.drop_table("market_cap_exposures")
    op.drop_table("region_exposures")
    op.drop_table("sector_exposures")
    op.drop_table("fund_performance_snapshots")
    op.drop_table("historical_prices")
    op.drop_table("holdings")
    op.drop_table("assets")
    op.drop_table("funds")
    op.drop_table("benchmarks")
