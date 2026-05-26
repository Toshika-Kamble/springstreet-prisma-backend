# One-command setup and run for Windows (PowerShell)
param(
    [Parameter(Position = 0)]
    [ValidateSet("setup", "seed", "etl", "dev", "all")]
    [string]$Command = "all"
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

function Ensure-Venv {
    if (-not (Test-Path ".venv\Scripts\python.exe")) {
        Write-Host "Creating virtual environment..."
        python -m venv .venv
    }
    & .\.venv\Scripts\pip install -q -r requirements.txt
}

function Ensure-Env {
    if (-not (Test-Path ".env")) {
        Copy-Item .env.example .env
        Write-Host "Created .env from .env.example (SQLite default)"
    }
    New-Item -ItemType Directory -Force -Path data | Out-Null
}

function Invoke-Setup {
    Ensure-Venv
    Ensure-Env
    Write-Host "Running database migrations..."
    & .\.venv\Scripts\alembic upgrade head
    Write-Host "Setup complete."
}

function Invoke-Seed {
    Ensure-Venv
    Ensure-Env
    & .\.venv\Scripts\python -m scripts.seed_data
}

function Invoke-Etl {
    Ensure-Venv
    Ensure-Env
    & .\.venv\Scripts\python -m scripts.run_etl
}

function Invoke-Dev {
    Ensure-Venv
    Ensure-Env
    Write-Host "Starting API at http://127.0.0.1:8000"
    Write-Host "Docs: http://127.0.0.1:8000/docs"
    & .\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
}

switch ($Command) {
    "setup" { Invoke-Setup }
    "seed"  { Invoke-Setup; Invoke-Seed }
    "etl"   { Invoke-Etl }
    "dev"   { Invoke-Dev }
    "all"   { Invoke-Setup; Invoke-Seed; Invoke-Dev }
}
