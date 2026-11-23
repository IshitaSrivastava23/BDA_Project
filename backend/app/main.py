from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .service import AnalyticsService, DatasetUnavailableError


ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT / "HospitalAnalytics" / "data" / "raw"
configured_dataset = os.getenv("DATASET_PATH", "").strip()
if configured_dataset:
    DATASET_PATH = configured_dataset
else:
    preferred_dataset = RAW_DATA_DIR / "Hospital_Inpatient_Discharges_2016.csv"
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))
    DATASET_PATH = str(preferred_dataset if preferred_dataset.exists() else (csv_files[0] if csv_files else preferred_dataset))
PROCESSED_DATASET_PATH = os.getenv(
    "PROCESSED_DATASET_PATH",
    str(ROOT / "HospitalAnalytics" / "data" / "processed" / "cleaned.parquet"),
)

service = AnalyticsService(Path(DATASET_PATH), Path(PROCESSED_DATASET_PATH))
app = FastAPI(
    title="Healthcare Big Data Analytics API",
    version="1.0.0",
    description="Data-driven APIs for the SPARCS 2016 inpatient discharge project.",
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
