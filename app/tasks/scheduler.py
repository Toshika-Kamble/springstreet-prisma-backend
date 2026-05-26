"""APScheduler background jobs."""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.etl.pipeline import DailyETLPipeline

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def run_daily_etl() -> None:
    logger.info("Scheduled daily ETL job started")
    db = SessionLocal()
    try:
        pipeline = DailyETLPipeline(db)
        pipeline.run()
    except Exception:
        logger.exception("Scheduled ETL job failed")
        db.rollback()
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler | None:
    global _scheduler
    settings = get_settings()
    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled via configuration")
        return None
    if _scheduler is not None:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        run_daily_etl,
        trigger=CronTrigger(
            hour=settings.etl_cron_hour,
            minute=settings.etl_cron_minute,
        ),
        id="daily_etl",
        name="Daily market data & analytics refresh",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "Scheduler started: daily ETL at %02d:%02d UTC",
        settings.etl_cron_hour,
        settings.etl_cron_minute,
    )
    return _scheduler


def shutdown_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler shut down")
