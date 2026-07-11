"""Tests for the preprocessing + model pipeline."""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.config import FEATURES, TARGET
from src.data import clean
from src.preprocessing import build_preprocessor


def _fit_pipeline(raw_df):
    df = clean(raw_df)
    pipe = Pipeline(
        steps=[
            ("preprocess", build_preprocessor()),
            ("model", LogisticRegression(max_iter=1000)),
        ]
    )
    pipe.fit(df[FEATURES], df[TARGET])
    return pipe, df


def test_pipeline_fits_and_predicts(raw_df):
    pipe, df = _fit_pipeline(raw_df)
    preds = pipe.predict(df[FEATURES])
    assert len(preds) == len(df)
    assert set(np.unique(preds)).issubset({0, 1})


def test_pipeline_outputs_probabilities(raw_df):
    pipe, df = _fit_pipeline(raw_df)
    proba = pipe.predict_proba(df[FEATURES])
    assert proba.shape == (len(df), 2)
    assert np.allclose(proba.sum(axis=1), 1.0)


def test_preprocessor_handles_missing_values(raw_df):
    pipe, df = _fit_pipeline(raw_df)
    # Rows 0/1 had missing ca/thal; prediction must still succeed.
    assert pipe.predict(df[FEATURES].iloc[:2]).shape == (2,)
