"""Central configuration: paths, column definitions, and constants.

Keeping every hard-coded name in one place makes the pipeline reproducible
and easy to reason about across data, training, and serving code.
"""
from __future__ import annotations

from pathlib import Path

# --- Paths -----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
RAW_DATA_PATH = DATA_DIR / "heart_disease_raw.csv"
CLEAN_DATA_PATH = DATA_DIR / "heart_disease_clean.csv"
MODEL_PATH = MODELS_DIR / "model.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"

# --- Dataset ---------------------------------------------------------------
# UCI Heart Disease (Cleveland). The raw file has no header; these are the
# canonical column names documented by the UCI repository.
COLUMN_NAMES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "target",
]

TARGET = "target"

# Feature groups for the preprocessing pipeline.
NUMERIC_FEATURES = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_FEATURES = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Reproducibility
RANDOM_STATE = 42

# MLflow
MLFLOW_EXPERIMENT = "heart-disease-classification"
