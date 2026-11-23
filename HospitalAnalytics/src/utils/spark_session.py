"""Spark session construction."""

from pyspark.sql import SparkSession

from src.config import PipelineConfig


def create_spark_session(config: PipelineConfig) -> SparkSession:
    """Create a local-friendly Spark session with explicit settings."""
    return (
        SparkSession.builder.appName(config.app_name)
        .master(config.master)
        .config("spark.driver.memory", config.driver_memory)
        .config("spark.sql.shuffle.partitions", str(config.shuffle_partitions))
        .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
        .getOrCreate()
    )
