"""Descriptive Spark aggregations."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def overall_summary(data: DataFrame) -> DataFrame:
    """Summarize record counts and numeric LoS distribution."""
    return data.agg(
        F.count(F.lit(1)).alias("total_records"),
        F.sum(F.when(F.col("los_status") == "numeric", 1).otherwise(0)).alias(
            "valid_numeric_los_records"
        ),
        F.sum(F.when(F.col("los_status") == "top_coded_120_plus", 1).otherwise(0)).alias(
            "top_coded_120_plus_records"
        ),
        F.avg("LoS").alias("average_los"),
        F.min("LoS").alias("minimum_los"),
        F.max("LoS").alias("maximum_numeric_los"),
        F.expr("percentile_approx(LoS, 0.5)").alias("median_los"),
    )


def grouped_los_summary(data: DataFrame, group_column: str, count_name: str) -> DataFrame:
    """Aggregate valid LoS statistics by one categorical field."""
    return (
        data.filter(F.col("LoS").isNotNull())
        .groupBy(group_column)
        .agg(
            F.count("*").alias(count_name),
            F.avg("LoS").alias("average_los"),
            F.min("LoS").alias("minimum_los"),
            F.max("LoS").alias("maximum_los"),
        )
        .orderBy(F.desc(count_name))
    )


def admission_summary(data: DataFrame) -> DataFrame:
    return grouped_los_summary(data, "type_of_admission", "admission_count")


def age_summary(data: DataFrame) -> DataFrame:
    return grouped_los_summary(data, "age_group", "discharge_count")


def severity_summary(data: DataFrame) -> DataFrame:
    return grouped_los_summary(
        data, "apr_severity_of_illness_description", "record_count"
    )


def hospital_summary(data: DataFrame) -> DataFrame:
    group_column = "facility_id" if "facility_id" in data.columns else "hospital_county"
    return grouped_los_summary(data, group_column, "discharge_count")
