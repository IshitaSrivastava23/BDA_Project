"""CSV/Parquet ingestion and schema validation."""

from pathlib import Path
import re

from pyspark.sql import DataFrame, SparkSession

from src.config import COLUMN_ALIASES, REQUIRED_COLUMNS


def normalize_column_name(name: str) -> str:
    """Convert a source header to a stable snake_case name."""
    normalized = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return COLUMN_ALIASES.get(normalized, normalized)


def normalize_columns(data: DataFrame) -> DataFrame:
    """Rename source columns without changing their values."""
    renamed = data
    used: set[str] = set()
    for column in data.columns:
        target = normalize_column_name(column)
        if target in used and target != column:
            target = f"{target}_source"
        used.add(target)
        if target != column:
            renamed = renamed.withColumnRenamed(column, target)
    return renamed


def load_dataset(spark: SparkSession, input_path: Path, input_format: str = "csv") -> DataFrame:
    """Load a dataset and fail explicitly for a missing or unsupported path."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input dataset does not exist: {input_path}")
    if input_format not in {"csv", "parquet"}:
        raise ValueError(f"Unsupported input format: {input_format}")
    reader = spark.read
    if input_format == "csv":
        data = reader.option("header", True).option("inferSchema", True).option(
            "mode", "FAILFAST"
        ).csv(str(input_path))
    else:
        data = reader.parquet(str(input_path))
    return normalize_columns(data)


def validate_required_columns(data: DataFrame) -> None:
    """Ensure all model and target fields are available."""
    missing = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(missing)
            + f". Available columns: {', '.join(data.columns)}"
        )
