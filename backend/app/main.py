from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import re
from threading import Lock

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .service import AnalyticsService, DatasetUnavailableError


ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT / "HospitalAnalytics" / "data" / "raw"
configured_dataset = os.getenv("DATASET_PATH", "").strip()
if configured_dataset:
    DATASET_PATH = configured_dataset
else:
    preferred_dataset = RAW_DATA_DIR / "Hospital_Inpatient_Discharges_2023.csv"
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))
    DATASET_PATH = str(preferred_dataset if preferred_dataset.exists() else (csv_files[0] if csv_files else preferred_dataset))
PROCESSED_DATASET_PATH = os.getenv(
    "PROCESSED_DATASET_PATH",
    str(ROOT / "HospitalAnalytics" / "data" / "processed" / "cleaned.parquet"),
)

service = AnalyticsService(Path(DATASET_PATH), Path(PROCESSED_DATASET_PATH))


class SparkQuery(BaseModel):
    sql: str = Field(min_length=1, max_length=4000)


class SparkManager:
    def __init__(self, dataset_path: Path) -> None:
        self.dataset_path = dataset_path
        self.spark = None
        self.frame = None
        self.lock = Lock()
        self.error: str | None = None

    def status(self) -> dict[str, Any]:
        java_home = os.getenv("JAVA_HOME", "")
        return {
            "available": self.dataset_path.exists(),
            "dataset": str(self.dataset_path),
            "java_home": java_home,
            "session_active": self.spark is not None,
            "error": self.error,
        }

    def start(self) -> None:
        if self.spark is not None:
            return
        with self.lock:
            if self.spark is not None:
                return
            try:
                os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
                os.environ.setdefault("PYSPARK_PYTHON", os.getenv("PYTHON_EXECUTABLE", os.sys.executable))
                from pyspark.sql import SparkSession

                self.spark = (
                    SparkSession.builder.appName("HealthcareBDAInteractiveSQL")
                    .master("local[2]")
                    .config("spark.driver.memory", "2g")
                    .config("spark.sql.shuffle.partitions", "8")
                    .config("spark.ui.enabled", "false")
                    .getOrCreate()
                )
                self.spark.sparkContext.setLogLevel("ERROR")
                self.frame = (
                    self.spark.read.option("header", True).option("inferSchema", True)
                    .csv(str(self.dataset_path))
                )
                self.frame.createOrReplaceTempView("hospital_data")
                self.error = None
            except Exception as exc:
                self.spark = None
                self.error = f"{type(exc).__name__}: {exc}"
                raise

    def query(self, sql: str) -> dict[str, Any]:
        statement = sql.strip().rstrip(";").strip()
        first = re.split(r"\s+", statement, maxsplit=1)[0].lower()
        if first not in {"select", "with", "show", "describe", "desc"}:
            raise ValueError("Only read-only SELECT, WITH, SHOW, DESCRIBE, or DESC statements are allowed.")
        if ";" in statement:
            raise ValueError("Submit one SQL statement at a time.")
        forbidden = re.search(r"\b(insert|update|delete|drop|alter|create|truncate|merge|call)\b", statement, re.I)
        if forbidden:
            raise ValueError("Write operations and schema changes are not allowed.")
        self.start()
        if self.spark is None:
            raise RuntimeError(self.error or "Spark session could not be started.")
        limited = statement
        if first in {"select", "with"}:
            if re.search(r"\blimit\s+\d+\b", limited, re.I):
                limited = re.sub(r"\blimit\s+(\d+)\b", lambda match: f"LIMIT {min(int(match.group(1)), 1000)}", limited, flags=re.I)
        result = self.spark.sql(limited)
        rows = [row.asDict(recursive=True) for row in result.limit(1000).collect()]
        return {"columns": list(result.columns), "rows": rows, "row_count": len(rows)}


spark_manager = SparkManager(Path(DATASET_PATH))
app = FastAPI(
    title="Healthcare Big Data Analytics API",
    version="1.0.0",
    description="Data-driven APIs for the SPARCS 2023 inpatient discharge project.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list({
        origin
        for origin in (
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            os.getenv("FRONTEND_ORIGIN", "").strip(),
        )
        if origin
    }),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _unavailable() -> HTTPException:
    return HTTPException(
        status_code=503,
        detail=(
            "The SPARCS dataset is not configured. Download the source CSV and set "
            "DATASET_PATH, or place it in HospitalAnalytics/data/raw/."
        ),
    )


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "data_available": service.available, "dataset_path": str(service.dataset_path)}


@app.get("/api/dashboard/summary")
def dashboard_summary() -> dict[str, Any]:
    try:
        return service.dashboard_summary()
    except DatasetUnavailableError:
        return {
            "data_available": False,
            "message": "Dataset unavailable. Configure DATASET_PATH to enable live metrics.",
            "metrics": {},
            "insights": [],
        }


@app.get("/api/dataset/metadata")
def dataset_metadata() -> dict[str, Any]:
    return service.metadata()


@app.get("/api/dataset/columns")
def dataset_columns() -> dict[str, Any]:
    return service.columns()


@app.get("/api/dataset/sample")
def dataset_sample(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: str = Query("", max_length=100),
    age_group: str = Query(""),
    admission_type: str = Query(""),
    severity: str = Query(""),
) -> dict[str, Any]:
    try:
        return service.sample(page, page_size, search, age_group, admission_type, severity)
    except DatasetUnavailableError:
        raise _unavailable()


@app.get("/api/analytics/overview")
def analytics_overview(
    age_group: str = Query(""),
    admission_type: str = Query(""),
    severity: str = Query(""),
) -> dict[str, Any]:
    try:
        return service.analytics(age_group, admission_type, severity)
    except DatasetUnavailableError:
        raise _unavailable()


@app.get("/api/processing/overview")
def processing_overview() -> dict[str, Any]:
    return service.processing_overview()


@app.get("/api/insights")
def insights() -> dict[str, Any]:
    try:
        return {"data_available": True, "items": service.insights()}
    except DatasetUnavailableError:
        return {"data_available": False, "items": []}


@app.get("/api/spark/status")
def spark_status() -> dict[str, Any]:
    return spark_manager.status()


@app.post("/api/spark/query")
def spark_query(request: SparkQuery) -> dict[str, Any]:
    if not spark_manager.dataset_path.exists():
        raise HTTPException(status_code=503, detail="Configure DATASET_PATH with a local SPARCS CSV.")
    try:
        return spark_manager.query(request.sql)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Spark query failed: {exc}")


@app.get("/api/figures")
def figures() -> dict[str, Any]:
    figures_dir = ROOT / "HospitalAnalytics" / "outputs" / "figures"
    return {
        "items": [
            {"name": path.stem, "url": f"/figures/{path.name}"}
            for path in sorted(figures_dir.glob("*.png"))
        ]
    }


@app.get("/figures/{filename}")
def figure(filename: str):
    from fastapi.responses import FileResponse

    figures_dir = ROOT / "HospitalAnalytics" / "outputs" / "figures"
    path = (figures_dir / filename).resolve()
    if path.parent != figures_dir.resolve() or path.suffix.lower() != ".png" or not path.exists():
        raise HTTPException(status_code=404, detail="Figure not found")
    return FileResponse(path)
