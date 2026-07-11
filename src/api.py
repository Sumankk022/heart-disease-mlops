"""FastAPI serving app for the heart-disease classifier.

Endpoints:
    GET  /health   -> liveness probe
    GET  /metrics  -> Prometheus metrics (request counts + latency)
    POST /predict  -> single-patient prediction with confidence
"""
from __future__ import annotations

import logging
import time
from functools import lru_cache

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from starlette.responses import Response

from src.config import FEATURES, MODEL_PATH
from src.schemas import PatientFeatures, PredictionResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("heart-disease-api")

# --- Prometheus metrics ----------------------------------------------------
REQUEST_COUNT = Counter(
    "api_requests_total", "Total API requests", ["endpoint", "method", "status"]
)
REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds", "Request latency (s)", ["endpoint"]
)
PREDICTIONS = Counter(
    "predictions_total", "Predictions by outcome", ["outcome"]
)

app = FastAPI(
    title="Heart Disease Prediction API",
    description="Predicts heart-disease risk from patient health data.",
    version="1.0.0",
)


@lru_cache(maxsize=1)
def get_model():
    """Load the trained pipeline once and cache it."""
    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Model not found at {MODEL_PATH}. Run `python -m src.train` first."
        )
    logger.info("Loading model from %s", MODEL_PATH)
    return joblib.load(MODEL_PATH)


@app.middleware("http")
async def log_and_measure(request: Request, call_next):
    """Log every request and record latency + status for monitoring."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    endpoint = request.url.path
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(elapsed)
    REQUEST_COUNT.labels(
        endpoint=endpoint, method=request.method, status=response.status_code
    ).inc()
    logger.info(
        "%s %s -> %s (%.1f ms)",
        request.method,
        endpoint,
        response.status_code,
        elapsed * 1000,
    )
    return response


@app.get("/health")
def health() -> dict:
    """Liveness probe; also reports whether the model is loaded."""
    return {"status": "ok", "model_loaded": MODEL_PATH.exists()}


@app.get("/metrics")
def metrics() -> Response:
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict", response_model=PredictionResponse)
def predict(features: PatientFeatures) -> PredictionResponse:
    """Predict heart-disease risk for a single patient."""
    try:
        model = get_model()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    row = pd.DataFrame([features.model_dump()])[FEATURES]
    pred = int(model.predict(row)[0])
    proba = model.predict_proba(row)[0]
    confidence = float(proba[pred])

    PREDICTIONS.labels(outcome="disease" if pred else "no_disease").inc()

    return PredictionResponse(
        prediction=pred,
        label="Heart disease" if pred else "No heart disease",
        confidence=round(confidence, 4),
    )
