# Hospital Length of Stay Analytics

Apache Spark/PySpark analytics for the New York State SPARCS 2023 Inpatient Discharges dataset. The project cleans and summarizes inpatient discharge data and trains a leakage-aware Random Forest regression model for numeric length of stay.

## Status

The repository contains the complete modular implementation and focused unit tests. The public dataset is intentionally not included; place a local CSV in `data/raw/` or pass its path with `--input`.

## Quick start

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest
python -m src.main --input data/raw/Hospital_Inpatient_Discharges_2023.csv
```

PySpark requires a compatible Java runtime (Java 8, 11, or 17 are commonly supported by the selected Spark release). Confirm `java -version` before running the pipeline.

## Dataset

Download the de-identified New York State SPARCS 2023 Inpatient Discharges CSV from the New York State Health Data repository. The exact file is not committed because it is large and externally maintained. See [data/README.md](data/README.md) for placement and schema notes.

## What the pipeline does

1. Reads and validates the CSV with Spark.
2. Normalizes column names while retaining source columns.
3. Removes exact duplicate rows and reports missing values.
4. Classifies `Length of Stay` values as numeric, top-coded `120+`, or invalid/missing. Top-coded values are never converted to 120.
5. Writes the cleaned DataFrame to Parquet.
6. Produces Spark aggregations for overall, age, admission, severity, diagnosis, and hospital views.
7. Builds a Spark ML pipeline using `StringIndexer`, `OneHotEncoder`, `VectorAssembler`, and `RandomForestRegressor`.
8. Trains only on valid numeric LoS rows and excludes leakage-prone charges, costs, disposition, and top-coded rows.
9. Writes JSON metrics, actual-vs-predicted samples, CSV reports, and PNG charts.

Run only selected phases when reusing an existing cleaned Parquet dataset:

```powershell
python -m src.main --input data/raw/input.csv --analysis-only
python -m src.main --input data/processed/cleaned.parquet --model-only --input-format parquet
```

## Project layout

```text
data/raw/                 Local source CSV (ignored by Git)
data/processed/           Cleaned Parquet (ignored by Git)
models/                   Saved Spark model (ignored by Git)
outputs/reports/          Spark aggregation CSV files
outputs/metrics/          Evaluation JSON
outputs/figures/          PNG charts
src/                      Application modules
tests/                    Small synthetic-data unit tests
```

## Installation and execution

Install Python dependencies with `pip install -r requirements.txt`. For a normal laptop, the CLI defaults to local Spark with a conservative driver memory setting:

```powershell
python -m src.main --input .\data\raw\Hospital_Inpatient_Discharges_2023.csv --output-dir .\outputs
```

Useful options include `--master`, `--shuffle-partitions`, `--analysis-only`, `--model-only`, `--no-cache`, and `--log-level`. Use `python -m src.main --help` for the full list.

## Outputs

- `data/processed/cleaned.parquet`: cleaned source rows with `LoS` and `los_status`.
- `outputs/reports/*.csv`: aggregated analysis tables.
- `outputs/metrics/model_metrics.json`: MAE, RMSE, R², counts, and timings from the actual run.
- `outputs/reports/actual_vs_predicted.csv`: bounded sample of model predictions.
- `outputs/figures/*.png`: required analytical and model charts.
- `models/random_forest_pipeline`: fitted Spark ML pipeline.

The application never fabricates model metrics. A complete run requires the dataset and compatible Java/Spark dependencies.

## Methodology and limitations

Numeric LoS statistics exclude invalid/missing values and separately report the `120+` top-coded category. Categorical missing values are represented as `Unknown`. Spark transformations are fitted on the training split only. The model uses age group, admission type, severity of illness, and risk of mortality; it intentionally excludes total charges, total costs, patient disposition, and other post-discharge leakage.

This is an academic analytics project, not a clinically validated model. Historical, de-identified data may contain reporting bias and does not represent current hospital operations. It does not provide medical advice, clinical recommendations, or real-time hospital occupancy information.

## Tests

Tests use small local Spark DataFrames and do not require the 2.34-million-row source file:

```powershell
python -m pytest -q
```

## GitHub setup

```powershell
git remote add origin https://github.com/<account>/<repository>.git
git push -u origin main
```

Raw data, Parquet, Spark model directories, figures, metrics, and virtual environments are excluded by `.gitignore`.
