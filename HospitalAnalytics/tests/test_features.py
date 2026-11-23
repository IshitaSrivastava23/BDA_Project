from src.ingestion.load_data import normalize_columns, validate_required_columns
from src.ml.feature_engineering import FEATURE_COLUMNS, build_feature_pipeline, training_frame
from src.preprocessing.clean_data import clean_data


def test_required_columns_and_feature_transformation(spark):
    source = spark.createDataFrame(
        [
            ("Adult", "Emergency", "Minor", "Low", "2"),
            ("Child", "Elective", "Major", "High", "5"),
        ],
        [
            "Age Group",
            "Type of Admission",
            "APR Severity of Illness Description",
            "APR Risk of Mortality",
            "Length of Stay",
        ],
    )
    normalized = normalize_columns(source)
    validate_required_columns(normalized)
    cleaned, _ = clean_data(normalized)
    frame = training_frame(cleaned)
    assert frame.count() == 2
    transformed = build_feature_pipeline().fit(frame).transform(frame)
    assert transformed.select("features").first().features.size > 0
    assert all(column in frame.columns for column in FEATURE_COLUMNS)


def test_missing_required_column_is_reported(spark):
    source = spark.createDataFrame([("Adult",)], ["Age Group"])
    try:
        validate_required_columns(normalize_columns(source))
    except ValueError as error:
        assert "length_of_stay" in str(error)
    else:
        raise AssertionError("Expected required-column validation to fail")
