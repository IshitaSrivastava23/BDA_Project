"""Shared local Spark fixture for focused unit tests."""

import os

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
    session = (
        SparkSession.builder.master("local[2]")
        .appName("HospitalAnalyticsTests")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    yield session
    session.stop()
