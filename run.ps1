# One-command local runner for Windows PowerShell.
#
# Usage (from the project root):
#   .\run.ps1            # setup venv, install deps, train if needed, start API
#   .\run.ps1 -Train     # force retrain the model
#   .\run.ps1 -Mlflow    # also open the MLflow UI (separate window)
#
# If you get a script-execution error, run once in this shell:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

param(
    [switch]$Train,
    [switch]$Mlflow
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 1. Virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "==> Creating virtual environment (.venv)"
    python -m venv .venv
}
Write-Host "==> Activating .venv"
& ".\.venv\Scripts\Activate.ps1"

# 2. Dependencies (setuptools first: provides pkg_resources on Python 3.12+)
Write-Host "==> Installing dependencies"
python -m pip install --upgrade pip | Out-Null
python -m pip install "setuptools<81" | Out-Null
python -m pip install -r requirements.txt

# 3. Data + model
if (-not (Test-Path "data\heart_disease_raw.csv")) {
    Write-Host "==> Downloading dataset"
    python data\download_data.py
}
if ($Train -or -not (Test-Path "models\model.joblib")) {
    Write-Host "==> Training model"
    python -m src.train
} else {
    Write-Host "==> Model already present (use -Train to retrain)"
}

# 4. Optional MLflow UI in a new window
if ($Mlflow) {
    Write-Host "==> Launching MLflow UI at http://127.0.0.1:5000"
    Start-Process powershell -ArgumentList @(
        "-NoExit", "-Command",
        "& { Set-Location '$PSScriptRoot'; .\.venv\Scripts\Activate.ps1; python -m mlflow ui }"
    )
}

# 5. Start the API
Write-Host ""
Write-Host "==> Starting API at http://127.0.0.1:8000  (docs: http://127.0.0.1:8000/docs)"
Write-Host "    Press Ctrl+C to stop."
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
