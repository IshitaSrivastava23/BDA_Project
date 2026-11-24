# Data instructions

1. Download the New York State SPARCS 2023 Inpatient Discharges CSV from the official New York State Health Data repository.
2. Put the file in `data/raw/`, for example `data/raw/Hospital_Inpatient_Discharges_2023.csv`.
3. Pass the exact path to the CLI:

```powershell
python -m src.main --input data/raw/Hospital_Inpatient_Discharges_2023.csv
```

The application validates required fields after normalizing headers. In particular, it needs a length-of-stay field and the four model predictors: Age Group, Type of Admission, APR Severity of Illness Description, and APR Risk of Mortality. Source columns are retained alongside normalized columns. Do not commit the source CSV or derived data.
