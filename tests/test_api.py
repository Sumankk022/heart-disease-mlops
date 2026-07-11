"""Tests for the FastAPI serving app."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src import api
from src.config import FEATURES, TARGET
from src.data import clean
from src.preprocessing import build_preprocessor

SAMPLE = {
    "age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233, "fbs": 1,
    "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 3,
    "ca": 0, "thal": 6,
}


def _train_stub(raw_df):
    df = clean(raw_df)
    pipe = Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            ("model", LogisticRegression(max_iter=1000)),
        ]
    )
    pipe.fit(df[FEATURES], df[TARGET])
    return pipe


def test_health():
    client = TestClient(api.app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_metrics_endpoint():
    client = TestClient(api.app)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "api_requests_total" in resp.text


def test_predict(monkeypatch, raw_df):
    model = _train_stub(raw_df)
    monkeypatch.setattr(api, "get_model", lambda: model)
    client = TestClient(api.app)

    resp = client.post("/predict", json=SAMPLE)
    assert resp.status_code == 200
    body = resp.json()
    assert body["prediction"] in (0, 1)
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["label"] in {"Heart disease", "No heart disease"}


def test_predict_validation_error():
    client = TestClient(api.app)
    bad = dict(SAMPLE, sex=5)  # out of allowed range
    resp = client.post("/predict", json=bad)
    assert resp.status_code == 422
