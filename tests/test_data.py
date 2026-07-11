"""Tests for data cleaning logic."""
from __future__ import annotations

import pandas as pd

from src.config import TARGET
from src.data import clean


def test_clean_binarizes_target(raw_df):
    cleaned = clean(raw_df)
    assert set(cleaned[TARGET].unique()).issubset({0, 1})


def test_clean_replaces_missing_markers(raw_df):
    cleaned = clean(raw_df)
    # '?' should become numeric NaN, not a literal string.
    assert cleaned["ca"].isna().sum() >= 1
    assert cleaned["thal"].isna().sum() >= 1
    assert pd.api.types.is_numeric_dtype(cleaned["ca"])


def test_clean_does_not_mutate_input(raw_df):
    before = raw_df.copy()
    clean(raw_df)
    pd.testing.assert_frame_equal(raw_df, before)
