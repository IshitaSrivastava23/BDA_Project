"""Command-line entry point for the hospital analytics pipeline."""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

from src.analysis.descriptive_analysis import (
    admission_summary,
    age_summary,
    hospital_summary,
    overall_summary,
    severity_summary,
)
from src.analysis.diagnosis_analysis import diagnosis_summary
from src.config import PipelineConfig
from src.ingestion.load_data import load_dataset, validate_required_columns
from src.ml.evaluate_model import evaluate_model, save_metrics
from src.ml.train_model import train_model
from src.preprocessing.clean_data import clean_data, save_cleaned_data
from src.utils.spark_session import create_spark_session
from src.visualization.generate_charts import (
    generate_analysis_charts,
    plot_actual_vs_predicted,
    plot_metrics,
)

LOGGER = logging.getLogger(__name__)


def _write_report(data, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data.write.mode("overwrite").option("header", True).csv(str(path))


def run_pipeline(args: argparse.Namespace) -> None:
    started = time.perf_counter()
    config = PipelineConfig(
        input_path=Path(args.input),
        output_dir=Path(args.output_dir),
        processed_dir=Path(args.processed_dir),
        model_dir=Path(args.model_dir),
        master=args.master,
        shuffle_partitions=args.shuffle_partitions,
        cache=not args.no_cache,
    )
    spark = create_spark_session(config)
    try:
        source = load_dataset(spark, config.input_path, args.input_format)
        validate_required_columns(source)
        LOGGER.info("Loaded %d records with %d columns", source.count(), len(source.columns))
        if args.model_only:
            if args.input_format != "parquet":
                raise ValueError("--model-only requires --input-format parquet")
            cleaned = source
        else:
            cleaned, missing = clean_data(source)
            if not args.analysis_only:
                _write_report(missing, config.output_dir / "reports" / "missing_values.csv")
                save_cleaned_data(cleaned, config.processed_dir / "cleaned.parquet")
        if config.cache:
            cleaned.cache()
        reports = {
            "overall": overall_summary(cleaned),
            "age": age_summary(cleaned),
            "admission": admission_summary(cleaned),
            "severity": severity_summary(cleaned),
            "diagnosis": diagnosis_summary(cleaned),
            "hospital": hospital_summary(cleaned),
        }
        for name, report in reports.items():
            _write_report(report, config.output_dir / "reports" / f"{name}.csv")
        generate_analysis_charts(cleaned, reports, config.output_dir / "figures")
        if not args.analysis_only:
            model, train, test, training_seconds = train_model(cleaned, config.model_dir)
            metrics, predictions = evaluate_model(model, test)
            metrics.update(
                {
                    "training_seconds": training_seconds,
                    "execution_seconds": time.perf_counter() - started,
                    "training_records": train.count(),
                    "testing_records": test.count(),
                }
            )
            save_metrics(metrics, config.output_dir / "metrics" / "model_metrics.json")
            predictions.limit(5000).write.mode("overwrite").option("header", True).csv(
                str(config.output_dir / "reports" / "actual_vs_predicted.csv")
            )
            plot_actual_vs_predicted(predictions, config.output_dir / "figures" / "actual_vs_predicted.png")
            plot_metrics(metrics, config.output_dir / "figures" / "model_metrics.png")
    finally:
        spark.stop()
        LOGGER.info("Pipeline finished in %.2f seconds", time.perf_counter() - started)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV or Parquet dataset path")
    parser.add_argument("--input-format", choices=("csv", "parquet"), default="csv")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--model-dir", default="models/random_forest_pipeline")
    parser.add_argument("--master", default="local[*]")
    parser.add_argument("--shuffle-partitions", type=int, default=8)
    parser.add_argument("--analysis-only", action="store_true")
    parser.add_argument("--model-only", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    return parser


if __name__ == "__main__":
    parsed = build_parser().parse_args()
    logging.basicConfig(level=getattr(logging, parsed.log_level.upper()), format="%(levelname)s %(message)s")
    run_pipeline(parsed)
