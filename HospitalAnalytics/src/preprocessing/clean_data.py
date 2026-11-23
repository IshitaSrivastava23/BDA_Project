"""Spark-based cleaning, missing-value reporting, and LoS classification."""

from pathlib import Path

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType


def missing_value_counts(data: DataFrame) -> DataFrame:
    """Return one row with null/blank counts for every column."""
    return data.select(
        *[
            F.sum(
                F.when(F.col(column).isNull() | (F.trim(F.col(column).cast("string")) == ""), 1)
                .otherwise(0)
            ).alias(column)
            for column in data.columns
        ]
    )


def clean_data(data: DataFrame) -> tuple[DataFrame, DataFrame]:
    """Deduplicate, fill categoricals, and classify the source LoS field.

    Returns the cleaned frame and a one-row missing-value report for the original frame.
    """
    missing = missing_value_counts(data)
    cleaned = data.dropDuplicates()
    categorical = [
        "age_group",
        "type_of_admission",
        "apr_severity_of_illness_description",
        "apr_risk_of_mortality",
        "ccs_diagnosis_description",
        "hospital_county",
    ]
    for column in categorical:
        if column in cleaned.columns:
            cleaned = cleaned.withColumn(
                column,
                F.when(
                    F.col(column).isNull() | (F.trim(F.col(column).cast("string")) == ""),
                    F.lit("Unknown"),
                ).otherwise(F.trim(F.col(column).cast("string"))),
            )

    raw_los = F.trim(F.col("length_of_stay").cast("string"))
    numeric_los = F.when(raw_los.rlike(r"^[0-9]+(?:\.[0-9]+)?$"), raw_los.cast(DoubleType()))
    cleaned = (
        cleaned.withColumn(
            "los_status",
            F.when(raw_los == "120+", F.lit("top_coded_120_plus"))
            .when(numeric_los.isNotNull(), F.lit("numeric"))
            .otherwise(F.lit("invalid_or_missing")),
        )
        .withColumn("LoS", numeric_los)
    )
    return cleaned, missing


def save_cleaned_data(data: DataFrame, path: Path) -> None:
    """Persist the cleaned DataFrame as Parquet."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data.write.mode("overwrite").parquet(str(path))
