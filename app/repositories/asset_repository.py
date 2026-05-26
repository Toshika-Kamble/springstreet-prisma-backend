from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset


class AssetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_symbol(self, symbol: str) -> Asset | None:
        stmt = select(Asset).where(Asset.symbol == symbol.upper())
        return self.db.scalars(stmt).first()

    def upsert(self, asset: Asset) -> Asset:
        existing = self.get_by_symbol(asset.symbol)
        if existing:
            for attr in ("name", "asset_type", "sector", "region", "market_cap_bucket"):
                val = getattr(asset, attr, None)
                if val is not None:
                    setattr(existing, attr, val)
            self.db.flush()
            return existing
        self.db.add(asset)
        self.db.flush()
        return asset
