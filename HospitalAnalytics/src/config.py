"""Configuration and column conventions for the analytics pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import Final

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "age_group",
    "type_of_admission",
    "apr_severity_of_illness_description",
    "apr_risk_of_mortality",
    "length_of_stay",
)

COLUMN_ALIASES: Final[dict[str, str]] = {
    "age_group": "age_group",
    "type_of_admission": "type_of_admission",
    "apr_severity_of_illness_description": "apr_severity_of_illness_description",
    "apr_severity_of_illness": "apr_severity_of_illness_description",
    "apr_risk_of_mortality": "apr_risk_of_mortality",
    "length_of_stay": "length_of_stay",
    "ccs_diagnosis_code": "ccs_diagnosis_code",
    "ccs_diagnosis_description": "ccs_diagnosis_description",
    "hospital_county": "hospital_county",
    "facility_id": "facility_id",
}


@dataclass(frozen=True)
class PipelineConfig:
    """Paths and Spark settings used by one pipeline execution."""

    input_path: Path
    output_dir: Path = Path("outputs")
    processed_dir: Path = Path("data/processed")
    model_dir: Path = Path("models/random_forest_pipeline")
    master: str = "local[*]"
    app_name: str = "HospitalLengthOfStayAnalytics"
    driver_memory: str = "2g"
    shuffle_partitions: int = 8
    cache: bool = True
