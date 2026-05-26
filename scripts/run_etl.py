"""Manually trigger the daily ETL pipeline."""

from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.etl.pipeline import DailyETLPipeline

setup_logging()


def main() -> None:
    db = SessionLocal()
    try:
        stats = DailyETLPipeline(db).run()
        print(f"ETL complete: {stats}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
