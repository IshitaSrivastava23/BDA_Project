from src.preprocessing.clean_data import clean_data


def _rows(spark):
    return spark.createDataFrame(
        [
            ("Adult", "Emergency", "Minor", " low ", "3"),
            ("Adult", "Emergency", "Minor", " low ", "120+"),
            (None, "Elective", None, None, "not recorded"),
            ("Adult", "Emergency", "Minor", " low ", "3"),
        ],
        [
            "Age Group",
            "Type of Admission",
            "APR Severity of Illness Description",
            "APR Risk of Mortality",
            "Length of Stay",
        ],
    )


def test_clean_data_classifies_los_and_removes_duplicates(spark):
    from src.ingestion.load_data import normalize_columns

    cleaned, _ = clean_data(normalize_columns(_rows(spark)))
    assert cleaned.count() == 3
    statuses = {row.los_status for row in cleaned.select("los_status").collect()}
    assert statuses == {"numeric", "top_coded_120_plus", "invalid_or_missing"}
    top = cleaned.filter("los_status = 'top_coded_120_plus'").first()
    assert top.LoS is None


def test_clean_data_fills_missing_categories(spark):
    from src.ingestion.load_data import normalize_columns

    cleaned, _ = clean_data(normalize_columns(_rows(spark)))
    row = cleaned.filter("los_status = 'invalid_or_missing'").first()
    assert row.age_group == "Unknown"
    assert row.apr_severity_of_illness_description == "Unknown"
    assert row.apr_risk_of_mortality == "Unknown"
