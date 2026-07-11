"""Shared pytest fixtures: a small synthetic dataset mirroring the schema."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.config import COLUMN_NAMES


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """A tiny raw-style frame including '?' missing markers and 0-4 target."""
    rng = np.random.default_rng(0)
    n = 40
    data = {
        "age": rng.integers(30, 70, n).astype(float),
        "sex": rng.integers(0, 2, n).astype(float),
        "cp": rng.integers(1, 5, n).astype(float),
        "trestbps": rng.integers(100, 180, n).astype(float),
        "chol": rng.integers(150, 320, n).astype(float),
        "fbs": rng.integers(0, 2, n).astype(float),
        "restecg": rng.integers(0, 3, n).astype(float),
        "thalach": rng.integers(90, 200, n).astype(float),
        "exang": rng.integers(0, 2, n).astype(float),
        "oldpeak": rng.uniform(0, 4, n).round(1),
        "slope": rng.integers(1, 4, n).astype(float),
        "ca": rng.integers(0, 4, n).astype(object),
        "thal": rng.choice([3.0, 6.0, 7.0], n).astype(object),
        "target": rng.integers(0, 5, n).astype(float),
    }
    df = pd.DataFrame(data, columns=COLUMN_NAMES)
    # Inject a couple of missing markers like the real UCI file.
    df.loc[0, "ca"] = "?"
    df.loc[1, "thal"] = "?"
    return df
