from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.db.session import SessionLocal, engine
from app.tasks.scheduler import shutdown_scheduler, start_scheduler

setup_logging()
settings = get_settings()

if settings.database_url.startswith("sqlite"):
    Path("data").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Investment factsheet backend — funds, holdings, performance, and exposure analytics.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.exception_handler(AppException)
async def handle_app_exception(_request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/health")
def health_check() -> dict[str, str]:
    db_status = "ok"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except OperationalError:
        db_status = "unavailable"
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "environment": settings.app_env,
        "database": db_status,
        "dialect": engine.dialect.name,
    }


@app.exception_handler(OperationalError)
async def handle_db_error(_request: Request, exc: OperationalError) -> JSONResponse:
    detail = (
        "Database is not available. Run: .\\run.ps1 setup  (or alembic upgrade head)"
    )
    if not settings.database_url.startswith("sqlite"):
        detail += " — ensure PostgreSQL is running and DATABASE_URL is correct."
    return JSONResponse(status_code=503, content={"detail": detail, "error": str(exc.orig)})
