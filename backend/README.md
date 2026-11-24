# Healthcare analytics API

From `D:\Projectss\BDA`:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
$env:DATASET_PATH = "D:\Projectss\BDA\HospitalAnalytics\data\raw\Hospital_Inpatient_Discharges_2023.csv"
uvicorn backend.app.main:app --reload --port 8001
```

The API never fabricates metrics. Without a local CSV or cleaned Parquet file, summary endpoints return an explicit unavailable state.
