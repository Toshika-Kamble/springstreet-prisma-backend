"""Health and landing pages — HTML for browsers, JSON for monitoring tools."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.db.session import SessionLocal, engine

router = APIRouter(tags=["health"])
settings = get_settings()


def _collect_health() -> dict:
    db_status = "ok"
    fund_count: int | None = None
    error: str | None = None

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            fund_count = db.scalar(text("SELECT COUNT(*) FROM funds"))
    except SQLAlchemyError as exc:
        db_status = "unavailable"
        error = str(exc.orig) if hasattr(exc, "orig") else str(exc)

    overall = "ok" if db_status == "ok" else "degraded"
    return {
        "status": overall,
        "service": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
        "database": db_status,
        "dialect": engine.dialect.name,
        "fund_count": fund_count,
        "scheduler_enabled": settings.scheduler_enabled,
        "error": error,
        "links": {
            "docs": "/docs",
            "redoc": "/redoc",
            "funds_api": f"{settings.api_v1_prefix}/funds",
            "health_json": "/health?format=json",
        },
    }


def _wants_html(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    if "format=json" in str(request.url.query):
        return False
    if "format=html" in str(request.url.query):
        return True
    return "text/html" in accept and "application/json" not in accept.split(",")[0]


def _health_html(data: dict) -> str:
    ok = data["status"] == "ok"
    status_color = "#16a34a" if ok else "#ca8a04"
    db_color = "#16a34a" if data["database"] == "ok" else "#dc2626"
    fund_line = (
        f'<p><strong>Funds in database:</strong> {data["fund_count"]}</p>'
        if data["fund_count"] is not None
        else ""
    )
    error_line = (
        f'<p style="color:#dc2626"><strong>Error:</strong> {data["error"]}</p>'
        if data.get("error")
        else ""
    )
    links = data["links"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{data["service"]} — Health</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; color: #1e293b; }}
    h1 {{ font-size: 1.5rem; margin-bottom: 0.25rem; }}
    .badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; color: white; font-weight: 600; }}
    .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem 1.25rem; margin: 1rem 0; }}
    a {{ color: #2563eb; }}
    ul {{ line-height: 1.8; }}
    .muted {{ color: #64748b; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <h1>{data["service"]}</h1>
  <p class="muted">Version {data["version"]} · {data["environment"]}</p>
  <p><span class="badge" style="background:{status_color}">API {data["status"].upper()}</span></p>
  <div class="card">
    <p><strong>Database:</strong> <span style="color:{db_color}">{data["database"]}</span> ({data["dialect"]})</p>
    {fund_line}
    <p><strong>Scheduler:</strong> {"enabled" if data["scheduler_enabled"] else "disabled"}</p>
    {error_line}
  </div>
  <h2>Quick links</h2>
  <ul>
    <li><a href="{links["docs"]}">API docs (Swagger)</a></li>
    <li><a href="{links["redoc"]}">API docs (ReDoc)</a></li>
    <li><a href="{links["funds_api"]}">List funds (JSON)</a></li>
    <li><a href="{links["health_json"]}">Health check (JSON)</a></li>
  </ul>
  <p class="muted">Monitoring tools: <code>GET /health</code> with <code>Accept: application/json</code> or <code>?format=json</code></p>
</body>
</html>"""


def _landing_html(data: dict) -> str:
    links = data["links"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{data["service"]}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; color: #1e293b; }}
    h1 {{ font-size: 1.75rem; }}
    a {{ color: #2563eb; }}
    ul {{ line-height: 1.9; }}
    .muted {{ color: #64748b; }}
  </style>
</head>
<body>
  <h1>{data["service"]}</h1>
  <p class="muted">Investment factsheet backend — funds, holdings, performance, exposures.</p>
  <ul>
    <li><a href="/health">Health status</a></li>
    <li><a href="{links["docs"]}">Interactive API docs</a></li>
    <li><a href="{links["funds_api"]}">GET {links["funds_api"]}</a> — list funds</li>
  </ul>
  <p class="muted">Example: <code>/api/v1/funds/SPY</code> · <code>/api/v1/funds/SPY/performance</code></p>
</body>
</html>"""


@router.get("/health", include_in_schema=True)
def health_check(request: Request) -> Response:
    data = _collect_health()
    if _wants_html(request):
        return HTMLResponse(_health_html(data), status_code=200 if data["status"] == "ok" else 503)
    return JSONResponse(
        content=data,
        status_code=200 if data["status"] == "ok" else 503,
    )


@router.get("/", include_in_schema=False)
def landing(request: Request) -> Response:
    data = _collect_health()
    if _wants_html(request):
        return HTMLResponse(_landing_html(data))
    return JSONResponse(
        content={
            "message": settings.app_name,
            "status": data["status"],
            **data["links"],
        }
    )
