
from pyspark.sql import SparkSession
from pathlib import Path

# 1. Initialize Spark
spark = (
    SparkSession.builder
    .appName("Healthcare Big Data Analytics")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("\n========== PYSPARK SQL DEMONSTRATION ==========\n")

# 2. Load the SPARCS dataset
file_path = r"D:\Projectss\BDA\HospitalAnalytics\data\raw\H~ospital_Inpatient_Discharges_(SPARCS_De-Identified)__2023_20261101.csv"
raw_dir = Path(r"D:\Projectss\BDA\HospitalAnalytics\data\raw")
preferred = raw_dir / "Hospital_Inpatient_Discharges_2023.csv"
file_path = str(preferred if preferred.exists() else next(raw_dir.glob("*.csv"), preferred))

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(file_path)
)

# 3. Display dataset information
print("Total number of records:", df.count())

print("\nDataset Schema:")
df.printSchema()

print("\nFirst 5 records:")
df.show(5, truncate=False)

# 4. Register DataFrame as a SQL temporary view
df.createOrReplaceTempView("hospital_data")

print("\nSQL VIEW CREATED SUCCESSFULLY!")

# QUERY 1: Count hospital admissions by admission type
print("\nQUERY 1: Admissions by Type")

result1 = spark.sql("""
    SELECT
        `Type of Admission`,
        COUNT(*) AS Total_Admissions
    FROM hospital_data
    GROUP BY `Type of Admission`
    ORDER BY Total_Admissions DESC
""")

result1.show(truncate=False)

# QUERY 2: Average Length of Stay by illness severity
# Excludes the 120+ category because its exact value is unknown.

print("\nQUERY 2: Average Length of Stay by Severity")

result2 = spark.sql("""
    SELECT
        `APR Severity of Illness Description`,
        COUNT(*) AS Patient_Count,
        ROUND(
            AVG(
                CASE
                    WHEN TRIM(`Length of Stay`) RLIKE '^[0-9]+$'
                    THEN CAST(TRIM(`Length of Stay`) AS DOUBLE)
                    ELSE NULL
                END
            ), 2
        ) AS Average_Stay_Days
    FROM hospital_data
    GROUP BY `APR Severity of Illness Description`
    ORDER BY Average_Stay_Days DESC
""")

result2.show(truncate=False)

# QUERY 3: Average Length of Stay by age group

print("\nQUERY 3: Average Length of Stay by Age Group")

result3 = spark.sql("""
    SELECT
        `Age Group`,
        ROUND(
            AVG(
                CASE
                    WHEN TRIM(`Length of Stay`) RLIKE '^[0-9]+$'
                    THEN CAST(TRIM(`Length of Stay`) AS DOUBLE)
                    ELSE NULL
                END
            ), 2
        ) AS Average_Stay_Days
    FROM hospital_data
    GROUP BY `Age Group`
    ORDER BY Average_Stay_Days DESC
""")

result3.show(truncate=False)

print("\n========== DEMONSTRATION COMPLETED ==========")

spark.stop()
