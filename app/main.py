import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import setup_logging
from app.db.session import SessionLocal, engine
from app.tasks.scheduler import shutdown_scheduler, start_scheduler

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

if settings.database_url.startswith("sqlite"):
    Path("data").mkdir(parents=True, exist_ok=True)


def _verify_database() -> None:
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        logger.info("Database connected (%s)", engine.dialect.name)
    except SQLAlchemyError as exc:
        logger.error(
            "Database unavailable: %s. Run: .\\run.ps1 setup  (or alembic upgrade head)",
            exc,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _verify_database()
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


@app.exception_handler(SQLAlchemyError)
async def handle_database_error(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
    detail = (
        "Database error. Run: .\\run.ps1 setup  (or alembic upgrade head && python -m scripts.seed_data)"
    )
    if not settings.database_url.startswith("sqlite"):
        detail += " Ensure PostgreSQL is running and DATABASE_URL is correct."
    else:
        detail += " Restart the API after changing .env (stop uvicorn, then .\\run.ps1 dev)."
    return JSONResponse(
        status_code=503,
        content={"detail": detail, "error": str(exc.orig) if hasattr(exc, "orig") else str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s", request.url.path)
    content: dict = {"detail": "Internal server error"}
    if settings.debug:
        content["error"] = str(exc)
    return JSONResponse(status_code=500, content=content)


@app.get("/health")
def health_check() -> dict[str, str]:
    db_status = "ok"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        db_status = "unavailable"
        logger.warning("Health check DB error: %s", exc)

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "environment": settings.app_env,
        "database": db_status,
        "dialect": engine.dialect.name,
    }


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "docs": "/docs",
        "api": settings.api_v1_prefix,
        "funds": f"{settings.api_v1_prefix}/funds",
    }
