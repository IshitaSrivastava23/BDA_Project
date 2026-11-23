"""Model evaluation and metric persistence."""

import json
from pathlib import Path
from typing import Any

from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql import DataFrame


def evaluate_model(model: Any, test: DataFrame) -> tuple[dict[str, float], DataFrame]:
    """Calculate actual metrics from predictions."""
    predictions = model.transform(test).select("LoS", "prediction")
    metrics: dict[str, float] = {}
    for metric, name in (("mae", "mae"), ("rmse", "rmse"), ("r2", "r2")):
        evaluator = RegressionEvaluator(labelCol="LoS", predictionCol="prediction", metricName=metric)
        metrics[name] = float(evaluator.evaluate(predictions))
    return metrics, predictions


def save_metrics(metrics: dict[str, Any], path: Path) -> None:
    """Write JSON metrics with stable, human-readable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
