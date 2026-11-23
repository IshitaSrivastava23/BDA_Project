"""Diagnosis and hospital-level aggregations."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def diagnosis_summary(data: DataFrame) -> DataFrame:
    """Summarize diagnosis categories, preferring CCS code when available."""
    group_column = "ccs_diagnosis_code" if "ccs_diagnosis_code" in data.columns else "ccs_diagnosis_description"
    return (
        data.groupBy(group_column)
        .agg(
            F.count("*").alias("discharge_count"),
            F.avg("LoS").alias("average_los"),
        )
        .orderBy(F.desc("discharge_count"))
    )
