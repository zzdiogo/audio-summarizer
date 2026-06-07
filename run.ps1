# Start Audio Summarizer API
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "Created .env - edit with your API key before summarizing." -ForegroundColor Yellow
}

.\.venv\Scripts\Activate.ps1
$env:HF_HUB_DISABLE_SYMLINKS = "1"
Write-Host "Open http://localhost:8000 in your browser" -ForegroundColor Green
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
