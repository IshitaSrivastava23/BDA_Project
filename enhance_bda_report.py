from __future__ import absolute_import

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import hashlib
import shutil
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent
SOURCE_DOCX = ROOT / "BDA_Report_Final_Reference_Style.docx"
RAW_DIR = ROOT / "HospitalAnalytics" / "data" / "raw"
OUTPUT_DIR = ROOT / "BDA_Report_Enhanced"
VIS_DIR = OUTPUT_DIR / "Visualizations"
OUTPUT_DOCX = OUTPUT_DIR / "BDA_Report_Enhanced.docx"
OUTPUT_PDF = OUTPUT_DIR / "BDA_Report_Enhanced.pdf"
SUMMARY = OUTPUT_DIR / "Modification_Summary.txt"


def find_dataset() -> Path:
    preferred = RAW_DIR / "Hospital_Inpatient_Discharges_2023.csv"
    if preferred.exists():
        return preferred
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError("No CSV dataset was found in HospitalAnalytics/data/raw")
    return files[0]


def style_caption(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(2)
    paragraph.paragraph_format.space_after = Pt(8)
    for run in paragraph.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0, 0, 0)


def add_figure(doc, path: Path, caption: str, width=6.2):
    image_paragraph = doc.add_paragraph()
    image_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    image_paragraph.paragraph_format.keep_with_next = True
    image_paragraph.paragraph_format.space_before = Pt(8)
    image_paragraph.paragraph_format.space_after = Pt(3)
    image_paragraph.add_run().add_picture(str(path), width=Inches(width))

    caption_paragraph = doc.add_paragraph()
    caption_paragraph.add_run(caption)
    style_caption(caption_paragraph)


def save_barh(output: Path, labels, values, title, xlabel, color="#2563EB", limit=None):
    labels = list(labels)
    values = list(values)
    if limit:
        labels = labels[:limit]
        values = values[:limit]
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    y = range(len(labels))
    ax.barh(list(y), values, color=color, edgecolor="#1D4ED8", linewidth=0.6)
    ax.set_yticks(list(y), labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    for i, value in enumerate(values):
        ax.text(value, i, f" {value:,.2f}" if isinstance(value, float) else f" {value:,}", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def generate_actual_visualizations(dataset: Path) -> dict:
    VIS_DIR.mkdir(parents=True, exist_ok=True)

    columns = [
        "Age Group", "Gender", "Type of Admission", "Length of Stay",
        "APR Severity of Illness Description", "CCS Diagnosis Description",
        "Facility Id", "Hospital County", "Payment Typology 1",
    ]
    age_counts = pd.Series(dtype="int64")
    gender_counts = pd.Series(dtype="int64")
    admission_counts = pd.Series(dtype="int64")
    severity_los_sum = pd.Series(dtype="float64")
    severity_los_count = pd.Series(dtype="int64")
    age_los_sum = pd.Series(dtype="float64")
    age_los_count = pd.Series(dtype="int64")
    admission_los_sum = pd.Series(dtype="float64")
    admission_los_count = pd.Series(dtype="int64")
    diagnosis_counts = pd.Series(dtype="int64")
    facility_counts = pd.Series(dtype="int64")
    payment_counts = pd.Series(dtype="int64")
    missing_counts = pd.Series(0, index=columns, dtype="int64")
    los_hist = pd.Series(dtype="int64")
    count_series = {
        "age": age_counts,
        "gender": gender_counts,
        "admission": admission_counts,
        "payment": payment_counts,
        "diagnosis": diagnosis_counts,
        "facility": facility_counts,
    }
    total_records = 0
    numeric_los_records = 0
    top_coded_records = 0

    for chunk in pd.read_csv(
        dataset,
        usecols=lambda name: name in columns,
        chunksize=100_000,
        low_memory=False,
        dtype=str,
    ):
        total_records += len(chunk)
        missing_counts = missing_counts.add(chunk.isna().sum().reindex(columns, fill_value=0), fill_value=0)

        for source, target in [
            ("Age Group", "age"), ("Gender", "gender"), ("Type of Admission", "admission"),
            ("Payment Typology 1", "payment"), ("CCS Diagnosis Description", "diagnosis"),
            ("Facility Id", "facility"),
        ]:
            if source not in chunk:
                continue
            safe = chunk[source].fillna("Unknown").astype(str).str.strip()
            safe = safe.mask(safe.eq(""), "Unknown")
            counts = safe.value_counts()
            count_series[target] = count_series[target].add(counts, fill_value=0)

        raw_los = chunk["Length of Stay"].astype("string").str.strip() if "Length of Stay" in chunk else pd.Series("", index=chunk.index, dtype="string")
        top_coded_records += int(
            raw_los.str.strip().str.replace(r"\s+", "", regex=True).eq("120+").sum()
        )
        los = pd.to_numeric(raw_los, errors="coerce")
        valid = los.notna()
        numeric_los_records += int(valid.sum())
        los_hist = los_hist.add(los[valid].clip(upper=30).round().value_counts(), fill_value=0)

        if "Age Group" in chunk:
            cats = chunk["Age Group"].fillna("Unknown").astype(str).str.strip()
            vals = los
            mask = vals.notna()
            age_los_sum = age_los_sum.add(pd.Series(vals[mask].values, index=cats[mask].values).groupby(level=0).sum(), fill_value=0)
            age_los_count = age_los_count.add(pd.Series(1, index=cats[mask].values).groupby(level=0).sum(), fill_value=0)

        if "Type of Admission" in chunk:
            cats = chunk["Type of Admission"].fillna("Unknown").astype(str).str.strip()
            vals = los
            mask = vals.notna()
            admission_los_sum = admission_los_sum.add(pd.Series(vals[mask].values, index=cats[mask].values).groupby(level=0).sum(), fill_value=0)
            admission_los_count = admission_los_count.add(pd.Series(1, index=cats[mask].values).groupby(level=0).sum(), fill_value=0)

        if "APR Severity of Illness Description" in chunk:
            cats = chunk["APR Severity of Illness Description"].fillna("Unknown").astype(str).str.strip()
            vals = los
            mask = vals.notna()
            severity_los_sum = severity_los_sum.add(pd.Series(vals[mask].values, index=cats[mask].values).groupby(level=0).sum(), fill_value=0)
            severity_los_count = severity_los_count.add(pd.Series(1, index=cats[mask].values).groupby(level=0).sum(), fill_value=0)

    age_counts = count_series["age"]
    gender_counts = count_series["gender"]
    admission_counts = count_series["admission"]
    diagnosis_counts = count_series["diagnosis"]
    facility_counts = count_series["facility"]
    payment_counts = count_series["payment"]
    age_group_los = (age_los_sum / age_los_count).dropna().sort_values()
    admission_los = (admission_los_sum / admission_los_count).dropna().sort_values()
    severity_los = (severity_los_sum / severity_los_count).dropna()
    severity_order = ["Minor", "Moderate", "Major", "Extreme"]
    severity_los = pd.Series({name: severity_los[name] for name in severity_order if name in severity_los.index})
    los_values = los_hist.sort_index()
    average_los = float(numeric_los_records and (sum(age_los_sum.values) / sum(age_los_count.values)))

    fig, ax = plt.subplots(figsize=(9, 6), dpi=200)
    ax.bar(los_values.index.astype(str), los_values.values, color="#2563EB", edgecolor="#1D4ED8")
    ax.set_xlabel("Length of Stay (days, 30+ grouped)")
    ax.set_ylabel("Discharge count")
    ax.set_title("Distribution of Numeric Length of Stay")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    los_chart = VIS_DIR / "14_actual_los_distribution.png"
    fig.savefig(los_chart, dpi=300, bbox_inches="tight")
    plt.close(fig)

    save_barh(
        VIS_DIR / "15_actual_age_los.png",
        age_group_los.index,
        age_group_los.values,
        "Average Length of Stay by Age Group",
        "Average stay (days)",
        color="#0891B2",
    )

    save_barh(
        VIS_DIR / "16_actual_severity_los.png",
        severity_los.index,
        severity_los.values,
        "Average Length of Stay by Illness Severity",
        "Average stay (days)",
        color="#D97706",
    )

    save_barh(
        VIS_DIR / "17_actual_admission_los.png",
        admission_los.index,
        admission_los.values,
        "Average Length of Stay by Admission Type",
        "Average stay (days)",
        color="#4F46E5",
    )

    save_barh(
        VIS_DIR / "18_actual_top_diagnoses.png",
        diagnosis_counts.sort_values(ascending=False).head(12).index,
        diagnosis_counts.sort_values(ascending=False).head(12).values,
        "Top Diagnosis Categories by Discharge Count",
        "Discharge count",
        color="#0284C7",
    )

    save_barh(
        VIS_DIR / "19_actual_missing_values.png",
        missing_counts.sort_values(ascending=False).head(10).index,
        missing_counts.sort_values(ascending=False).head(10).values,
        "Missing Values in Key Dataset Attributes",
        "Missing record count",
        color="#DC2626",
    )

    payment_chart = payment_counts.sort_values(ascending=False).head(10)
    save_barh(
        VIS_DIR / "20_actual_payment_typology.png",
        payment_chart.index,
        payment_chart.values,
        "Top Payment Typologies",
        "Discharge count",
        color="#7C3AED",
    )

    fig, ax = plt.subplots(figsize=(8, 5), dpi=200)
    sizes = [numeric_los_records, top_coded_records]
    labels = [f"Numeric LoS\n{numeric_los_records:,}", f"Top-coded 120+\n{top_coded_records:,}"]
    ax.pie(sizes, labels=labels, autopct="%1.3f%%", startangle=90, colors=["#2563EB", "#F59E0B"],
           wedgeprops={"edgecolor": "white"})
    ax.set_title("Length-of-Stay Target Classification")
    fig.tight_layout()
    los_status_chart = VIS_DIR / "21_actual_los_status.png"
    fig.savefig(los_status_chart, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return {
        "total_records": total_records,
        "numeric_los_records": numeric_los_records,
        "top_coded_records": top_coded_records,
        "average_los": average_los,
        "missing_counts": missing_counts,
    }


def create_unavailable_model_chart(path: Path):
    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
    ax.axis("off")
    ax.text(0.5, 0.64, "Random Forest Model Evaluation", ha="center", va="center",
            fontsize=16, fontweight="bold", color="#1E293B")
    ax.text(0.5, 0.48, "MAE, RMSE, R-squared, and actual-versus-predicted records\nare unavailable.",
            ha="center", va="center", fontsize=12, color="#475569")
    ax.text(0.5, 0.30, "No fitted model or evaluation output was found in the workspace.",
            ha="center", va="center", fontsize=10, style="italic", color="#991B1B")
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def replace_embedded_media(docx_path: Path, source_png: Path, replacement_png: Path):
    source_hash = hashlib.sha256(source_png.read_bytes()).hexdigest()
    temp_path = docx_path.with_suffix(".tmp.docx")
    replaced = False
    with ZipFile(docx_path, "r") as zin, ZipFile(temp_path, "w", ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith("word/media/") and hashlib.sha256(data).hexdigest() == source_hash:
                data = replacement_png.read_bytes()
                replaced = True
            zout.writestr(item, data)
    if replaced:
        temp_path.replace(docx_path)
    else:
        temp_path.unlink(missing_ok=True)
    return replaced


def enhance_report(stats: dict, dataset: Path):
    doc = Document(SOURCE_DOCX)

    for paragraph in list(doc.paragraphs):
        text = paragraph.text.strip()
        if text.startswith("Fig. 13. PySpark Random Forest"):
            paragraph.clear()
            run = paragraph.add_run("Fig. 13. Random Forest Model Evaluation Status: Metrics and Predictions Unavailable.")
            style_caption(paragraph)
        if text.startswith("Fig. 13 displays"):
            paragraph.clear()
            run = paragraph.add_run(
                "Fig. 13 states that MAE, RMSE, R-squared, and actual-versus-predicted outputs cannot be reported because no fitted model or evaluation artifact was found. This is intentionally not represented as a completed prediction result."
            )
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()
    heading = doc.add_paragraph()
    heading.paragraph_format.keep_with_next = True
    run = heading.add_run("Appendix A: Verified Actual-Dataset Visualizations")
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.font.bold = True

    note = doc.add_paragraph()
    note.add_run(
        f"These visualizations were generated directly from the live CSV dataset ({dataset.name}) "
        f"using chunk-based Pandas processing. The verified total is {stats['total_records']:,} records."
    )
    note.paragraph_format.line_spacing = 1.15

    appendix = [
        ("14_actual_los_distribution.png", "Fig. A1. Distribution of numeric Length of Stay values from the live dataset. Values of 30 or more are grouped at the upper end for readability."),
        ("15_actual_age_los.png", "Fig. A2. Average Length of Stay across age groups calculated from numeric stay values."),
        ("16_actual_severity_los.png", "Fig. A3. Average Length of Stay across APR severity groups calculated from numeric stay values."),
        ("17_actual_admission_los.png", "Fig. A4. Average Length of Stay across admission categories calculated from numeric stay values."),
        ("18_actual_top_diagnoses.png", "Fig. A5. Twelve diagnosis descriptions with the largest discharge counts in the live dataset."),
        ("19_actual_missing_values.png", "Fig. A6. Missing-value counts for the key attributes with the largest missing-value totals."),
        ("20_actual_payment_typology.png", "Fig. A7. Ten payment typologies with the largest discharge counts."),
        ("21_actual_los_status.png", "Fig. A8. Classification of the Length-of-Stay field into numeric and top-coded 120+ records."),
    ]
    for filename, caption in appendix:
        add_figure(doc, VIS_DIR / filename, caption)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT_DOCX)

    unavailable = VIS_DIR / "model_evaluation_unavailable.png"
    create_unavailable_model_chart(unavailable)
    source_fig12 = ROOT / "HospitalAnalytics" / "outputs" / "figures" / "fig12_actual_vs_predicted_los.png"
    replaced = replace_embedded_media(OUTPUT_DOCX, source_fig12, unavailable)

    return replaced


def convert_to_pdf():
    try:
        import win32com.client
    except ImportError:
        return False
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        document = word.Documents.Open(str(OUTPUT_DOCX))
        document.SaveAs(str(OUTPUT_PDF), FileFormat=17)
        document.Close(False)
        return OUTPUT_PDF.exists()
    finally:
        word.Quit()


def write_summary(dataset: Path, stats: dict, replaced_model_image: bool, pdf_created: bool):
    text = (
        "BDA Report Enhancement Modification Summary\n"
        "===========================================\n"
        f"Source report: {SOURCE_DOCX.name}\n"
        f"Final document: {OUTPUT_DOCX.name}\n"
        f"Source dataset: {dataset.name}\n"
        f"Verified record count: {stats['total_records']:,}\n"
        f"Numeric LoS records: {stats['numeric_los_records']:,}\n"
        f"Top-coded 120+ records: {stats['top_coded_records']:,}\n"
        "Sections improved: report appendix added; model-evaluation status corrected.\n"
        "Actual-data charts added: 8.\n"
        "Technical diagrams newly added: 0 (existing 13 academic figures retained).\n"
        "Screenshots incorporated: 0 (no project screenshots were present in the report workspace).\n"
        f"Simulated model image replaced: {'Yes' if replaced_model_image else 'Not detected'}.\n"
        f"PDF preview created: {'Yes' if pdf_created else 'No - Microsoft Word automation unavailable or conversion failed'}.\n"
        "Missing or unresolved: fitted Spark MLlib model metrics and actual-versus-predicted artifacts were not found, "
        "so no MAE, RMSE, R-squared, or prediction graph was fabricated.\n"
    )
    SUMMARY.write_text(text, encoding="utf-8")


def main():
    if not SOURCE_DOCX.exists():
        raise FileNotFoundError(f"Original report not found: {SOURCE_DOCX}")
    dataset = find_dataset()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stats = generate_actual_visualizations(dataset)
    replaced_model_image = enhance_report(stats, dataset)
    pdf_created = convert_to_pdf()
    write_summary(dataset, stats, replaced_model_image, pdf_created)
    print(f"Enhanced DOCX: {OUTPUT_DOCX}")
    print(f"PDF: {OUTPUT_PDF if pdf_created else 'not created'}")
    print(f"Visualizations: {VIS_DIR}")


if __name__ == "__main__":
    main()
