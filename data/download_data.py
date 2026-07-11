"""Download the UCI Heart Disease (Cleveland) dataset.

Usage:
    python data/download_data.py

The raw file is header-less and uses '?' for missing values; we attach the
canonical column names and save a CSV to ``data/heart_disease_raw.csv``.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import COLUMN_NAMES, RAW_DATA_PATH  # noqa: E402

DATA_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "heart-disease/processed.cleveland.data"
)


def download() -> Path:
    """Fetch the dataset and persist it as a labelled CSV."""
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading dataset from {DATA_URL}")
    with urllib.request.urlopen(DATA_URL, timeout=60) as resp:  # noqa: S310
        raw_text = resp.read().decode("utf-8")

    tmp = RAW_DATA_PATH.with_suffix(".tmp")
    tmp.write_text(raw_text, encoding="utf-8")

    df = pd.read_csv(tmp, header=None, names=COLUMN_NAMES)
    df.to_csv(RAW_DATA_PATH, index=False)
    tmp.unlink()

    print(f"Saved {len(df)} rows to {RAW_DATA_PATH}")
    return RAW_DATA_PATH


if __name__ == "__main__":
    download()
