"""Exploratory Data Analysis for the Heart Disease dataset.

Generates professional visualizations (target balance, histograms,
correlation heatmap) and saves them to ``reports/figures/``.

Usage:
    python -m src.eda
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless rendering
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

from src.config import NUMERIC_FEATURES, PROJECT_ROOT, TARGET  # noqa: E402
from src.data import load_clean  # noqa: E402

FIG_DIR = PROJECT_ROOT / "reports" / "figures"


def _save(fig, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / name
    fig.savefig(path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    print(f"Saved {path}")


def run() -> None:
    sns.set_theme(style="whitegrid")
    df = load_clean()

    # 1. Class balance
    fig, ax = plt.subplots(figsize=(5, 4))
    counts = df[TARGET].value_counts().sort_index()
    sns.barplot(x=["No disease", "Disease"], y=counts.values, ax=ax, palette="Set2")
    ax.set_title("Target Class Balance")
    ax.set_ylabel("Count")
    _save(fig, "class_balance.png")

    # 2. Numeric feature histograms
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for ax, col in zip(axes.ravel(), NUMERIC_FEATURES):
        sns.histplot(data=df, x=col, hue=TARGET, kde=True, ax=ax, palette="Set1")
        ax.set_title(col)
    for ax in axes.ravel()[len(NUMERIC_FEATURES):]:
        ax.axis("off")
    fig.suptitle("Numeric Feature Distributions by Target")
    _save(fig, "numeric_histograms.png")

    # 3. Correlation heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(df.corr(numeric_only=True), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("Feature Correlation Heatmap")
    _save(fig, "correlation_heatmap.png")

    print("EDA complete.")


if __name__ == "__main__":
    run()
