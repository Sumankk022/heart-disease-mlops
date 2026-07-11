#!/usr/bin/env bash
# One-command local runner for macOS / Linux.
#
# Usage (from the project root):
#   ./run.sh            # setup venv, install deps, train if needed, start API
#   ./run.sh --train    # force retrain the model
#   ./run.sh --mlflow   # also start the MLflow UI (background)
set -euo pipefail
cd "$(dirname "$0")"

FORCE_TRAIN=0
START_MLFLOW=0
for arg in "$@"; do
  case "$arg" in
    --train) FORCE_TRAIN=1 ;;
    --mlflow) START_MLFLOW=1 ;;
  esac
done

# 1. Virtual environment
if [ ! -d ".venv" ]; then
  echo "==> Creating virtual environment (.venv)"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

# 2. Dependencies (setuptools first: provides pkg_resources on Python 3.12+)
echo "==> Installing dependencies"
python -m pip install --upgrade pip >/dev/null
python -m pip install "setuptools<81" >/dev/null
python -m pip install -r requirements.txt

# 3. Data + model
if [ ! -f "data/heart_disease_raw.csv" ]; then
  echo "==> Downloading dataset"
  python data/download_data.py
fi
if [ "$FORCE_TRAIN" -eq 1 ] || [ ! -f "models/model.joblib" ]; then
  echo "==> Training model"
  python -m src.train
else
  echo "==> Model already present (use --train to retrain)"
fi

# 4. Optional MLflow UI
if [ "$START_MLFLOW" -eq 1 ]; then
  echo "==> Launching MLflow UI at http://127.0.0.1:5000 (background)"
  python -m mlflow ui >/tmp/mlflow_ui.log 2>&1 &
fi

# 5. Start the API
echo ""
echo "==> Starting API at http://127.0.0.1:8000  (docs: http://127.0.0.1:8000/docs)"
echo "    Press Ctrl+C to stop."
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
