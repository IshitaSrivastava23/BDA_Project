from src.analysis.descriptive_analysis import age_summary, overall_summary
from src.ingestion.load_data import normalize_columns
from src.preprocessing.clean_data import clean_data


def test_overall_and_age_aggregations(spark):
    source = spark.createDataFrame(
        [
            ("Adult", "Emergency", "Minor", "Low", "2"),
            ("Adult", "Emergency", "Minor", "Low", "4"),
            ("Child", "Elective", "Major", "High", "120+"),
        ],
        [
            "Age Group",
            "Type of Admission",
            "APR Severity of Illness Description",
            "APR Risk of Mortality",
            "Length of Stay",
        ],
    )
    cleaned, _ = clean_data(normalize_columns(source))
    summary = overall_summary(cleaned).first()
    assert summary.total_records == 3
    assert summary.valid_numeric_los_records == 2
    assert summary.top_coded_120_plus_records == 1
    assert summary.average_los == 3.0
    adult = age_summary(cleaned).filter("age_group = 'Adult'").first()
    assert adult.discharge_count == 2
    assert adult.average_los == 3.0
