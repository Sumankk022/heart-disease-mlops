# Heart Disease Prediction — MLOps Pipeline

End-to-end ML pipeline that predicts the risk of heart disease from patient
health data and serves it as a **Dockerized, monitored API**. Built for the
MLOps assignment: EDA → feature engineering → model training with experiment
tracking → tests → CI/CD → containerized serving → monitoring.

- **Dataset:** UCI Heart Disease (Cleveland), 303 records, 13 features + binary target.
- **Models:** Logistic Regression and Random Forest (best selected by CV ROC-AUC).
- **Serving:** FastAPI with `/predict`, `/health`, `/metrics`.
- **Deployment:** **Docker only** (single image, non-root, health-checked).

---

## TL;DR — one command

**Windows (PowerShell), from the project root:**
```powershell
.\run.ps1
```
**macOS / Linux:**
```bash
./run.sh
```
The script creates a virtual env, installs dependencies, trains the model if
needed, and starts the API. Then open **http://127.0.0.1:8000/docs**.

Options: `-Train`/`--train` to force retraining, `-Mlflow`/`--mlflow` to also
open the MLflow UI.

> Requires **Python 3.10+**. If PowerShell blocks the script, run once:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

### Or with Docker (one command)
```bash
docker compose up --build      # API at http://localhost:8000
```

### Or step by step
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.train                                  # train + save models/model.joblib
python -m uvicorn src.api:app --port 8000            # serve
# explore notebooks: jupyter notebook  (run 01 -> 02 -> 03)
```

Everything is pre-run once, so `models/model.joblib`, the executed notebooks,
and the report figures are already in the ZIP.

---

## Notebooks (data & ML workflow)

Run in order from the `notebooks/` folder:

| Notebook | Contents |
|----------|----------|
| `01_eda.ipynb` | Data download, cleaning, missing-value analysis, class balance, histograms, correlation heatmap, feature relationships |
| `02_modeling.ipynb` | Preprocessing pipeline, train/test split, LogReg + RandomForest tuned with `GridSearchCV`, metrics (accuracy/precision/recall/F1/ROC-AUC), confusion matrix, ROC curves, MLflow logging, saves best model |
| `03_inference.ipynb` | Loads the saved pipeline and predicts on sample patients |

The notebooks are shipped **already executed** (outputs embedded).

---

## Project structure

```
heart-disease-mlops/
├── data/
│   └── download_data.py        # fetches the UCI dataset
├── src/
│   ├── config.py               # paths, column defs, constants
│   ├── data.py                 # load + clean (missing values, binarize target)
│   ├── preprocessing.py        # ColumnTransformer (scale + one-hot + impute)
│   ├── eda.py                  # generates EDA figures
│   ├── train.py                # tune 2 models (GridSearchCV), MLflow, saves best
│   ├── schemas.py              # Pydantic request/response models
│   └── api.py                  # FastAPI serving app
├── tests/                      # pytest unit tests (data, model, API)
├── notebooks/                  # 01_eda, 02_modeling, 03_inference (executed)
├── .github/workflows/ci.yml    # lint -> test -> train -> docker build/smoke
├── reports/                    # written report + figures
├── screenshots/                # proof screenshots for submission
├── Dockerfile                  # multi-stage, non-root, healthcheck
├── requirements.txt
└── README.md
```

---

## Quickstart (local, from a clean setup)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Get the data
python data/download_data.py

# 2. Exploratory analysis (writes reports/figures/*.png)
python -m src.eda

# 3. Train + track experiments (writes models/model.joblib)
python -m src.train

# 4. (optional) inspect experiments
mlflow ui            # http://localhost:5000

# 5. Run tests + lint
flake8 src tests data
pytest

# 6. Serve the API locally
uvicorn src.api:app --reload
# docs: http://localhost:8000/docs
```

---

## Run with Docker (deployment)

Per the assignment, deployment is **Docker-only** — no Kubernetes/Helm.

```bash
# Train once so the model artifact exists, then build:
python data/download_data.py && python -m src.train
docker build -t heart-disease-api:latest .

# Run the container
docker run -d --name hd-api -p 8000:8000 heart-disease-api:latest

# Verify
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"age":63,"sex":1,"cp":1,"trestbps":145,"chol":233,"fbs":1,
       "restecg":2,"thalach":150,"exang":0,"oldpeak":2.3,"slope":3,"ca":0,"thal":6}'
```

Example response:

```json
{"prediction": 1, "label": "Heart disease", "confidence": 0.9438}
```

---

## API endpoints

| Method | Path       | Description                                  |
|--------|------------|----------------------------------------------|
| GET    | `/health`  | Liveness probe + model-loaded flag           |
| GET    | `/metrics` | Prometheus metrics (request counts, latency) |
| POST   | `/predict` | Prediction + confidence for one patient      |
| GET    | `/docs`    | Interactive Swagger UI                        |

---

## Experiment tracking (MLflow)

`src/train.py` logs both models to the `heart-disease-classification`
experiment: parameters, metrics (accuracy, precision, recall, ROC-AUC,
CV ROC-AUC), and the serialized pipeline. Launch `mlflow ui` to compare runs.

## Monitoring & logging

- Every request is logged (method, path, status, latency) via middleware.
- `/metrics` exposes Prometheus counters/histograms
  (`api_requests_total`, `api_request_latency_seconds`, `predictions_total`),
  ready to be scraped by Prometheus and visualized in Grafana.

## CI/CD

`.github/workflows/ci.yml` runs on every push/PR:
`flake8` → `pytest` → download data + `src.train` (uploads the model artifact)
→ build the Docker image → smoke-test the container's `/health` and `/predict`.
The pipeline fails on any lint, test, training, or build error.

## Model performance (held-out test set)

| Metric      | Random Forest (best) |
|-------------|----------------------|
| Accuracy    | 0.84                 |
| Precision   | 0.82                 |
| Recall      | 0.82                 |
| F1          | 0.82                 |
| ROC-AUC     | 0.94                 |
| CV ROC-AUC  | 0.90                 |

See [`reports/report.md`](reports/report.md) for the full write-up.
