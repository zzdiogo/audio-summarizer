# Arranca a API Meeting Summarizer
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "A criar ambiente virtual..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "Criado .env — edita com a tua OPENAI_API_KEY antes de resumir reuniões." -ForegroundColor Yellow
}

.\.venv\Scripts\Activate.ps1
$env:HF_HUB_DISABLE_SYMLINKS = "1"
Write-Host "API em http://localhost:8000/docs" -ForegroundColor Green
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
