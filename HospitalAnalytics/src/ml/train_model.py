"""Random Forest model training."""

from pathlib import Path
import time

from pyspark.ml import PipelineModel
from pyspark.ml.regression import RandomForestRegressor
from pyspark.sql import DataFrame

from src.ml.feature_engineering import build_feature_pipeline, training_frame


def train_model(
    data: DataFrame, model_path: Path, seed: int = 42
) -> tuple[PipelineModel, DataFrame, DataFrame, float]:
    """Fit the complete feature/model pipeline on an 80/20 deterministic split."""
    frame = training_frame(data)
    train, test = frame.randomSplit([0.8, 0.2], seed=seed)
    estimator = RandomForestRegressor(
        labelCol="LoS",
        featuresCol="features",
        numTrees=50,
        seed=seed,
    )
    pipeline = build_feature_pipeline()
    pipeline.setStages([*pipeline.getStages(), estimator])
    start = time.perf_counter()
    model = pipeline.fit(train)
    elapsed = time.perf_counter() - start
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.write().overwrite().save(str(model_path))
    return model, train, test, elapsed
