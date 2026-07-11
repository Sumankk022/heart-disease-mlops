"""Train, tune, and evaluate heart-disease classifiers with MLflow tracking.

For each candidate model we run ``GridSearchCV`` (5-fold, ROC-AUC) inside a
full sklearn Pipeline (preprocessing + estimator), evaluate the tuned model on
a held-out test set, log parameters/metrics/plots/model to MLflow, and persist
the best pipeline to ``models/``.

Usage:
    python -m src.train
"""
from __future__ import annotations

import json
from typing import Dict, Tuple

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mlflow  # noqa: E402
import mlflow.sklearn  # noqa: E402
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402

from src.config import (  # noqa: E402
    FEATURES,
    METRICS_PATH,
    MLFLOW_EXPERIMENT,
    MODEL_PATH,
    PROJECT_ROOT,
    RANDOM_STATE,
    TARGET,
)
from src.data import load_clean  # noqa: E402
from src.preprocessing import build_preprocessor  # noqa: E402

FIG_DIR = PROJECT_ROOT / "reports" / "figures"


def candidate_models() -> Dict[str, Tuple[object, dict]]:
    """Estimators + hyper-parameter grids for GridSearchCV.

    Grid keys are prefixed with ``model__`` because the estimator is the
    ``model`` step of the pipeline.
    """
    return {
        "logistic_regression": (
            LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
            {"model__C": [0.1, 1.0, 10.0]},
        ),
        "random_forest": (
            RandomForestClassifier(random_state=RANDOM_STATE),
            {
                "model__n_estimators": [100, 200],
                "model__max_depth": [4, 6, None],
            },
        ),
    }


def evaluate(pipeline: Pipeline, X_test, y_test) -> Dict[str, float]:
    """Headline classification metrics on the held-out test set."""
    preds = pipeline.predict(X_test)
    proba = pipeline.predict_proba(X_test)[:, 1]
    return {
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision": float(precision_score(y_test, preds)),
        "recall": float(recall_score(y_test, preds)),
        "f1": float(f1_score(y_test, preds)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
    }


def _save_plots(name: str, pipeline: Pipeline, X_test, y_test) -> list:
    """Save confusion-matrix and ROC-curve plots; return their paths."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    paths = []

    fig, ax = plt.subplots(figsize=(4, 4))
    ConfusionMatrixDisplay.from_estimator(
        pipeline, X_test, y_test, ax=ax, colorbar=False
    )
    ax.set_title(f"Confusion Matrix - {name}")
    cm_path = FIG_DIR / f"{name}_confusion_matrix.png"
    fig.savefig(cm_path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    paths.append(cm_path)

    fig, ax = plt.subplots(figsize=(5, 4))
    RocCurveDisplay.from_estimator(pipeline, X_test, y_test, ax=ax)
    ax.set_title(f"ROC Curve - {name}")
    roc_path = FIG_DIR / f"{name}_roc_curve.png"
    fig.savefig(roc_path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    paths.append(roc_path)

    return paths


def train() -> Dict[str, float]:
    """Run tuning + selection over all candidates and save the best model."""
    df = load_clean()
    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    best_name, best_pipeline, best_metrics, best_score = None, None, None, -1.0

    for name, (estimator, grid) in candidate_models().items():
        pipeline = Pipeline(
            steps=[("preprocess", build_preprocessor()), ("model", estimator)]
        )

        with mlflow.start_run(run_name=name):
            search = GridSearchCV(
                pipeline, grid, cv=5, scoring="roc_auc", n_jobs=-1
            )
            search.fit(X_train, y_train)
            tuned = search.best_estimator_

            metrics = evaluate(tuned, X_test, y_test)
            metrics["cv_roc_auc_best"] = float(search.best_score_)

            mlflow.log_param("model", name)
            mlflow.log_params(search.best_params_)
            mlflow.log_metrics(metrics)
            for plot_path in _save_plots(name, tuned, X_test, y_test):
                mlflow.log_artifact(str(plot_path), artifact_path="plots")
            mlflow.sklearn.log_model(
                tuned,
                artifact_path="model",
                skops_trusted_types=["numpy.dtype"],
            )

            print(f"[{name}] best_params={search.best_params_} {metrics}")

            if metrics["cv_roc_auc_best"] > best_score:
                best_name = name
                best_pipeline = tuned
                best_metrics = metrics
                best_score = metrics["cv_roc_auc_best"]

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_PATH)

    summary = {"best_model": best_name, **best_metrics}
    METRICS_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nBest model: {best_name} -> saved to {MODEL_PATH}")
    return summary


if __name__ == "__main__":
    train()
