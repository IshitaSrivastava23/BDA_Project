import pytest

from src.ingestion.load_data import load_dataset


def test_invalid_dataset_path_is_reported(spark, tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        load_dataset(spark, tmp_path / "missing.csv")
