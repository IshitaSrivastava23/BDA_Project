from __future__ import annotations

import re
from pathlib import Path
from threading import Lock
from typing import Any

import pandas as pd


class DatasetUnavailableError(RuntimeError):
    """Raised when no local dataset has been configured."""


ALIASES = {
    "age_group": "age_group",
    "type_of_admission": "type_of_admission",
    "apr_severity_of_illness": "apr_severity_of_illness_description",
    "apr_severity_of_illness_description": "apr_severity_of_illness_description",
    "apr_risk_of_mortality": "apr_risk_of_mortality",
    "length_of_stay": "length_of_stay",
    "ccs_diagnosis_code": "ccs_diagnosis_code",
    "ccs_diagnosis_description": "ccs_diagnosis_description",
    "hospital_county": "hospital_county",
    "facility_id": "facility_id",
    "gender": "gender",
}


def normalize(name: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return ALIASES.get(key, key)


class AnalyticsService:
    def __init__(self, dataset_path: Path, processed_path: Path) -> None:
        self.dataset_path = dataset_path
        self.processed_path = processed_path
        self._frame: pd.DataFrame | None = None
        self._lock = Lock()

    @property
    def available(self) -> bool:
        return self.dataset_path.exists() or self.processed_path.exists()

    def _load(self) -> pd.DataFrame:
        if self._frame is not None:
            return self._frame
        with self._lock:
            if self._frame is not None:
                return self._frame
            if self.processed_path.exists():
                frame = pd.read_parquet(self.processed_path)
            elif self.dataset_path.exists():
                frame = pd.read_csv(self.dataset_path, low_memory=False)
            else:
                raise DatasetUnavailableError()
            frame = frame.rename(columns={column: normalize(column) for column in frame.columns})
            if "length_of_stay" in frame.columns:
                raw = frame["length_of_stay"].astype("string").str.strip()
                frame["los_status"] = raw.map(
                    lambda value: "top_coded_120_plus"
                    if value == "120+"
                    else "numeric"
                    if pd.notna(value) and bool(re.fullmatch(r"\d+(?:\.\d+)?", str(value)))
                    else "invalid_or_missing"
                )
                frame["los"] = pd.to_numeric(raw.where(raw != "120+"), errors="coerce")
            self._frame = frame
            return frame

    @staticmethod
    def _json(value: Any) -> Any:
        if pd.isna(value):
            return None
        if hasattr(value, "item"):
            return value.item()
        return value

    def _filtered(self, age_group: str = "", admission_type: str = "", severity: str = "") -> pd.DataFrame:
        frame = self._load()
        filters = (
            ("age_group", age_group),
            ("type_of_admission", admission_type),
            ("apr_severity_of_illness_description", severity),
        )
        for column, value in filters:
            if value and column in frame.columns:
                frame = frame[frame[column].astype("string") == value]
        return frame

    def metadata(self) -> dict[str, Any]:
        if not self.available:
            return {
                "data_available": False,
                "source": "NYS SPARCS 2023 Inpatient Discharges",
                "message": "No local CSV or cleaned Parquet dataset was found.",
                "columns": [],
            }
        frame = self._load()
        return {
            "data_available": True,
            "source": "NYS SPARCS 2023 Inpatient Discharges",
            "rows": int(len(frame)),
            "column_count": int(len(frame.columns)),
            "columns": self.columns()["items"],
            "missing_values": {
                column: int(frame[column].isna().sum())
                for column in frame.columns
            },
        }

    def columns(self) -> dict[str, Any]:
        if not self.available:
            return {"data_available": False, "items": []}
        frame = self._load()
        return {
            "data_available": True,
            "items": [
                {
                    "name": column,
                    "dtype": str(frame[column].dtype),
                    "missing": int(frame[column].isna().sum()),
                    "unique_values": int(frame[column].nunique(dropna=True)),
                }
                for column in frame.columns
            ],
        }

    def sample(
        self, page: int, page_size: int, search: str, age_group: str, admission_type: str, severity: str
    ) -> dict[str, Any]:
        frame = self._filtered(age_group, admission_type, severity)
        safe = [
            column
            for column in (
                "age_group",
                "gender",
                "type_of_admission",
                "apr_severity_of_illness_description",
                "apr_risk_of_mortality",
                "ccs_diagnosis_description",
                "hospital_county",
                "los",
                "los_status",
            )
            if column in frame.columns
        ]
        if search:
            mask = frame[safe].astype("string").apply(
                lambda row: row.str.contains(search, case=False, na=False, regex=False).any(), axis=1
            )
            frame = frame[mask]
        total = len(frame)
        start = (page - 1) * page_size
        rows = frame.iloc[start : start + page_size][safe].copy().fillna("")
        return {"data_available": True, "page": page, "page_size": page_size, "total": total, "rows": rows.to_dict("records")}

    def analytics(self, age_group: str, admission_type: str, severity: str) -> dict[str, Any]:
        frame = self._filtered(age_group, admission_type, severity)
        result: dict[str, Any] = {"data_available": True, "filters": {"age_group": age_group, "admission_type": admission_type, "severity": severity}}
        result["options"] = {
            key: sorted(frame[column].dropna().astype(str).unique().tolist())[:100]
            for key, column in (
                ("age_groups", "age_group"),
                ("admission_types", "type_of_admission"),
                ("severities", "apr_severity_of_illness_description"),
            )
            if column in frame.columns
        }
        if "los" in frame.columns:
            valid = frame["los"].dropna()
            result["length_of_stay"] = {
                "average": self._json(valid.mean()) if not valid.empty else None,
                "median": self._json(valid.median()) if not valid.empty else None,
                "distribution": [
                    {"bucket": str(bucket), "count": int(count)}
                    for bucket, count in valid.clip(upper=30).round().value_counts().sort_index().items()
                ],
            }
        result["age"] = self._group(frame, "age_group", "average_los")
        result["admission"] = self._group(frame, "type_of_admission", "average_los")
        result["severity"] = self._group(frame, "apr_severity_of_illness_description", "average_los")
        hospital_column = "facility_id" if "facility_id" in frame.columns else "hospital_county"
        result["hospitals"] = self._group(frame, hospital_column, "discharge_count", limit=15)
        return result

    def _group(self, frame: pd.DataFrame, column: str, value_name: str, limit: int = 12) -> list[dict[str, Any]]:
        if column not in frame.columns:
            return []
        grouped = frame.assign(_category=frame[column].fillna("Unknown").astype(str))
        if value_name == "average_los" and "los" in grouped.columns:
            output = grouped.groupby("_category", as_index=False)["los"].mean().rename(columns={"los": value_name})
        else:
            output = grouped.groupby("_category", as_index=False).size().rename(columns={"size": value_name})
        output = output.sort_values(value_name, ascending=False).head(limit)
        return [{column: row["_category"], value_name: self._json(row[value_name])} for _, row in output.iterrows()]

    def dashboard_summary(self) -> dict[str, Any]:
        frame = self._load()
        metrics: dict[str, Any] = {
            "total_records": int(len(frame)),
            "columns": int(len(frame.columns)),
            "facilities": int(frame["facility_id"].nunique()) if "facility_id" in frame else None,
            "categories": int(frame["ccs_diagnosis_code"].nunique()) if "ccs_diagnosis_code" in frame else None,
            "average_los": self._json(frame["los"].mean()) if "los" in frame else None,
            "numeric_los_records": int(frame["los"].notna().sum()) if "los" in frame else None,
            "data_completeness": self._json(frame.notna().mean().mean() * 100),
        }
        return {"data_available": True, "metrics": metrics, "insights": self.insights()}

    def insights(self) -> list[dict[str, Any]]:
        frame = self._load()
        items: list[dict[str, Any]] = []
        for column, label in (
            ("age_group", "Age group"),
            ("type_of_admission", "Admission type"),
            ("apr_severity_of_illness_description", "Severity"),
        ):
            if column in frame.columns:
                counts = frame[column].fillna("Unknown").astype(str).value_counts()
                if not counts.empty:
                    items.append({"title": f"Most represented {label.lower()}", "metric": int(counts.iloc[0]), "value": str(counts.index[0]), "explanation": "Descriptive count from the selected dataset."})
        return items

    def processing_overview(self) -> dict[str, Any]:
        return {
            "steps": [
                {"name": "Ingestion", "purpose": "Read the CSV or cleaned Parquet dataset with schema inference and normalized headers.", "implementation": "src.ingestion.load_data.load_dataset"},
                {"name": "Cleaning", "purpose": "Remove exact duplicates, normalize categorical missing values, and classify Length of Stay.", "implementation": "src.preprocessing.clean_data.clean_data"},
                {"name": "Aggregation", "purpose": "Produce overall, age, admission, severity, diagnosis, and hospital summaries.", "implementation": "src.analysis.descriptive_analysis and diagnosis_analysis"},
                {"name": "Prediction", "purpose": "Train a leakage-aware Random Forest baseline on numeric Length of Stay rows.", "implementation": "src.ml.train_model.train_model"},
                {"name": "Visualization", "purpose": "Write bounded analytical reports and charts for review.", "implementation": "src.visualization.generate_charts"},
            ],
            "source_files": ["HospitalAnalytics/src/ingestion/load_data.py", "HospitalAnalytics/src/preprocessing/clean_data.py", "HospitalAnalytics/src/analysis/descriptive_analysis.py", "HospitalAnalytics/src/ml/train_model.py"],
        }
