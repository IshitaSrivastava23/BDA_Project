"""Small-result plotting helpers; only aggregated data is collected locally."""

from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pyspark.sql import DataFrame


def _plot_bar(data: DataFrame, category: str, value: str, title: str, path: Path) -> None:
    frame = data.select(category, value).toPandas()
    if frame.empty:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    ax = frame.plot.bar(x=category, y=value, figsize=(10, 6), legend=False, color="#2a6f97")
    ax.set_title(title)
    ax.set_xlabel(category.replace("_", " ").title())
    ax.set_ylabel(value.replace("_", " ").title())
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_los_distribution(data: DataFrame, path: Path) -> None:
    frame = data.filter(data.LoS.isNotNull()).select("LoS").toPandas()
    if frame.empty:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.hist(frame["LoS"], bins=40, color="#2a6f97", edgecolor="white")
    plt.title("Distribution of Numeric Length of Stay")
    plt.xlabel("Length of Stay (days)")
    plt.ylabel("Discharges")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_metrics(metrics: dict[str, float], path: Path) -> None:
    frame = pd.Series(metrics, dtype=float)
    path.parent.mkdir(parents=True, exist_ok=True)
    ax = frame.plot.bar(figsize=(8, 5), color="#61a5c2")
    ax.set_title("Random Forest Evaluation Metrics")
    ax.set_ylabel("Value")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_actual_vs_predicted(predictions: DataFrame, path: Path, limit: int = 5000) -> None:
    frame = predictions.limit(limit).toPandas()
    if frame.empty:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 6))
    plt.scatter(frame["LoS"], frame["prediction"], alpha=0.35, s=12, color="#2a6f97")
    plt.xlabel("Actual LoS")
    plt.ylabel("Predicted LoS")
    plt.title("Actual vs Predicted Length of Stay")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def generate_analysis_charts(data: DataFrame, reports: dict[str, DataFrame], figures_dir: Path) -> None:
    """Generate required charts from bounded aggregated or sampled data."""
    plot_los_distribution(data, figures_dir / "los_distribution.png")
    chart_specs: Iterable[tuple[str, str, str, str]] = (
        ("age", "age_group", "average_los", "Average LoS by Age Group"),
        ("admission", "type_of_admission", "average_los", "Average LoS by Admission Type"),
        (
            "severity",
            "apr_severity_of_illness_description",
            "average_los",
            "Average LoS by Severity of Illness",
        ),
    )
    for key, category, value, title in chart_specs:
        if key in reports:
            _plot_bar(reports[key], category, value, title, figures_dir / f"{key}_average_los.png")
    diagnosis = reports.get("diagnosis")
    if diagnosis is not None:
        diagnosis.limit(10).orderBy("discharge_count", ascending=False).toPandas().plot.bar(
            x=diagnosis.columns[0], y="discharge_count", figsize=(10, 6), legend=False
        )
        plt.title("Top 10 Diagnosis Categories by Discharge Count")
        plt.tight_layout()
        plt.savefig(figures_dir / "top_diagnosis_counts.png", dpi=160)
        plt.close()
        _plot_bar(
            diagnosis.limit(10),
            diagnosis.columns[0],
            "average_los",
            "Average LoS by Diagnosis Category",
            figures_dir / "diagnosis_average_los.png",
        )
