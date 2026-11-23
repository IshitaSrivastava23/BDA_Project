# Healthcare Big Data Analytics

This workspace contains the SPARCS 2016 inpatient discharge analytics pipeline and
an interactive web application around it. The application preserves the existing
PySpark implementation as the source of truth: it does not fabricate metrics when
the public dataset is absent.

## Run the application

The source CSV is intentionally not committed. Download the NYS SPARCS 2016
Inpatient Discharges dataset and place it at:

```text
HospitalAnalytics/data/raw/Hospital_Inpatient_Discharges_2016.csv
```

Start the API from `D:\Projectss\BDA`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

Start the frontend in a second terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:5173`. FastAPI documentation is available at
`http://localhost:8000/docs`.

Set `DATASET_PATH` or `PROCESSED_DATASET_PATH` when using a different CSV or the
cleaned Parquet output from the existing pipeline. The backend caches the loaded
frame and performs filtering and aggregation server-side. The frontend receives
only bounded samples and chart aggregates.

## Project areas

- `HospitalAnalytics/src/`: existing ingestion, cleaning, Spark SQL analysis,
  MLlib model, and visualization pipeline.
- `backend/app/`: FastAPI endpoints and the cached Pandas service used by the web
  application.
- `frontend/src/`: React/TypeScript dashboard, page navigation, filters, charts,
  tables, loading states, and unavailable-data states.

The dataset is historical and de-identified. Length of Stay values of `120+` are
kept as a top-coded category and are not treated as exactly 120 days. Results are
for academic historical analysis, not medical advice or a live clinical system.
