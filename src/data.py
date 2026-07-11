"""Data loading and cleaning for the Heart Disease dataset."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import CLEAN_DATA_PATH, COLUMN_NAMES, RAW_DATA_PATH, TARGET


def load_raw(path: Path | str = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw CSV, tolerating both labelled and header-less files."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run `python data/download_data.py` first."
        )
    df = pd.read_csv(path)
    if list(df.columns) != COLUMN_NAMES:
        # File saved without a header row.
        df = pd.read_csv(path, header=None, names=COLUMN_NAMES)
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw data: fix missing markers and binarize the target.

    - ``ca`` and ``thal`` use '?' for missing values in the UCI file.
    - The original target is 0-4 (severity); we collapse it to a binary
      presence/absence label as required by the problem statement.
    """
    df = df.copy()
    df = df.replace("?", pd.NA)

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df[TARGET] = (df[TARGET] > 0).astype(int)
    return df


def load_clean(save: bool = True) -> pd.DataFrame:
    """Convenience: load raw data, clean it, optionally cache the result."""
    df = clean(load_raw())
    if save:
        CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(CLEAN_DATA_PATH, index=False)
    return df
