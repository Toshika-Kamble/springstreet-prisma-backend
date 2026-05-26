from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.benchmark import Benchmark


class BenchmarkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_ticker(self, ticker: str) -> Benchmark | None:
        stmt = select(Benchmark).where(Benchmark.ticker == ticker.upper())
        return self.db.scalars(stmt).first()

    def upsert(self, benchmark: Benchmark) -> Benchmark:
        existing = self.get_by_ticker(benchmark.ticker)
        if existing:
            existing.name = benchmark.name
            if benchmark.description:
                existing.description = benchmark.description
            self.db.flush()
            return existing
        self.db.add(benchmark)
        self.db.flush()
        return benchmark
