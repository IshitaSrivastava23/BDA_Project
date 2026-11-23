"""Spark ML feature pipeline."""

from pyspark.ml import Pipeline
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.sql import DataFrame

FEATURE_COLUMNS = (
    "age_group",
    "type_of_admission",
    "apr_severity_of_illness_description",
    "apr_risk_of_mortality",
)


def build_feature_pipeline() -> Pipeline:
    """Create leakage-aware categorical encoding and vector assembly."""
    indexers = [
        StringIndexer(
            inputCol=column,
            outputCol=f"{column}_index",
            handleInvalid="keep",
        )
        for column in FEATURE_COLUMNS
    ]
    encoder = OneHotEncoder(
        inputCols=[f"{column}_index" for column in FEATURE_COLUMNS],
        outputCols=[f"{column}_encoded" for column in FEATURE_COLUMNS],
        handleInvalid="keep",
    )
    assembler = VectorAssembler(
        inputCols=[f"{column}_encoded" for column in FEATURE_COLUMNS],
        outputCol="features",
        handleInvalid="keep",
    )
    return Pipeline(stages=[*indexers, encoder, assembler])


def training_frame(data: DataFrame) -> DataFrame:
    """Select only numeric, non-top-coded targets and model predictors."""
    return data.filter(data.los_status == "numeric").filter(data.LoS.isNotNull()).select(
        *FEATURE_COLUMNS, "LoS"
    )
