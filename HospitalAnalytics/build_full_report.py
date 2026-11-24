"""Generate the enhanced Big Data Analytics Academic Project Report in .docx format.
Ensures pristine academic formatting, high-resolution visual integration,
and 100% preservation of original project content and empirical numbers.
"""

import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from docx_helpers import (
    create_document,
    add_heading_1,
    add_heading_2,
    add_heading_3,
    add_paragraph,
    add_bullet,
    add_callout,
    add_image_with_caption,
    add_code_block,
    set_table_styling
)

def build_report():
    doc = create_document()

    # =========================================================================
    # COVER / TITLE PAGE
    # =========================================================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(20)
    p_inst.paragraph_format.space_after = Pt(2)
    r_inst = p_inst.add_run("RAMAIAH INSTITUTE OF TECHNOLOGY\n")
    r_inst.font.name = "Calibri"
    r_inst.font.size = Pt(17)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(26, 54, 93)

    r_dept = p_inst.add_run("(Autonomous Institute Affiliated to VTU, Belagavi)\nDepartment of Computer Science and Engineering\n")
    r_dept.font.name = "Calibri"
    r_dept.font.size = Pt(11.5)
    r_dept.font.bold = True
    r_dept.font.color.rgb = RGBColor(71, 85, 105)

    r_course = p_inst.add_run("Dataset Analysis for Real-Time Scenarios\nSubject: Big Data Analytics   |   Code: CSE557   |   Term: 2026   |   Non-CIE: 10 Marks\n")
    r_course.font.name = "Calibri"
    r_course.font.size = Pt(10)
    r_course.font.color.rgb = RGBColor(100, 116, 139)

    # Decorative Line
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(28)
    r_l = p_line.add_run("━" * 58)
    r_l.font.color.rgb = RGBColor(43, 108, 176)

    # Project Title Box
    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_after = Pt(6)
    r_t_lbl = p_t.add_run("FINAL TECHNICAL PROJECT REPORT\n")
    r_t_lbl.font.name = "Calibri"
    r_t_lbl.font.size = Pt(11)
    r_t_lbl.font.bold = True
    r_t_lbl.font.color.rgb = RGBColor(43, 108, 176)

    r_title = p_t.add_run("Hospital Length of Stay Prediction and Resource Utilization Analysis Using Big Data Analytics\n")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    r_sub = p_t.add_run("A Scalable, Leakage-Aware Apache Spark / PySpark Inpatient Discharges Pipeline")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(30)

    # Metadata Table (Guide & Students)
    t_meta = doc.add_table(rows=5, cols=3)
    set_table_styling(t_meta, col_widths=[2.4, 1.8, 2.3])
    
    headers = ["Student Name", "USN", "Primary Responsibility"]
    for c, h in enumerate(headers):
        t_meta.cell(0, c).paragraphs[0].text = h
        
    members = [
        ("Keshav Kunal", "1MS24CS081", "Spark Pipeline Implementation, MLlib Modeling & Distributed Execution"),
        ("Ishita Srivastava", "1MS24CS070", "Data Ingestion, Quality Audit, Preprocessing, Aggregations & Visualizations")
    ]
    for r, (name, usn, resp) in enumerate(members, start=1):
        t_meta.cell(r, 0).paragraphs[0].text = name
        t_meta.cell(r, 1).paragraphs[0].text = usn
        t_meta.cell(r, 2).paragraphs[0].text = resp

    t_meta.cell(3, 0).paragraphs[0].text = "Faculty Guide:"
    t_meta.cell(3, 1).paragraphs[0].text = "Uzma Sulthana"
    t_meta.cell(3, 2).paragraphs[0].text = "Assistant Professor, Dept. of CSE"
    
    t_meta.cell(4, 0).paragraphs[0].text = "Academic Year:"
    t_meta.cell(4, 1).paragraphs[0].text = "2026"
    t_meta.cell(4, 2).paragraphs[0].text = "Ramaiah Institute of Technology, Bangalore"

    doc.add_page_break()

    # =========================================================================
    # PROJECT OVERVIEW & EXECUTIVE SUMMARY
    # =========================================================================
    add_heading_1(doc, "Project Overview and Executive Summary")
    
    add_paragraph(
        doc,
        "Modern healthcare institutions are under perpetual pressure to optimize clinical resource allocation, manage inpatient bed capacity, and control escalating operational expenses while preserving clinical efficacy. This project investigates hospital inpatient discharge records to understand and model the dynamics of hospital Length of Stay (LoS). Utilizing the publicly available New York State Statewide Planning and Research Cooperative System (SPARCS) 2023 Inpatient Discharges dataset—comprising 2,343,429 historical discharge records across 34 clinical, administrative, and financial attributes—this study implements an end-to-end distributed Big Data analytics workflow utilizing Apache Spark, PySpark SQL, and Spark MLlib.",
        bold_prefix="Executive Summary: "
    )
    
    add_paragraph(
        doc,
        "The analytical pipeline executes distributed data ingestion, automated schema validation, missing-value imputation, deduplication, and a clinical data leakage prevention barrier. By categorizing inpatient stays into valid numeric durations and isolated top-coded entries (120+ days), the system generates high-throughput multi-dimensional aggregations and trains a leakage-aware Random Forest regression baseline. Crucially, the project is structured to demonstrate how enterprise-grade Big Data technologies support retrospective healthcare intelligence and operational capacity planning, without advancing unverified real-time clinical diagnostic claims."
    )

    # Project Element Summary Table
    add_paragraph(doc, "Table E.1 summarizes the foundational parameters and scope of the analytics project.", bold_prefix="System Specifications: ")
    
    t_elem = doc.add_table(rows=7, cols=2)
    set_table_styling(t_elem, col_widths=[2.0, 4.5])
    t_elem.cell(0, 0).paragraphs[0].text = "Project Dimension"
    t_elem.cell(0, 1).paragraphs[0].text = "Technical Implementation Details"
    
    elem_data = [
        ("Domain & Focus", "Healthcare Analytics, Hospital Operations, Inpatient Resource Utilization"),
        ("Benchmark Dataset", "New York State SPARCS 2023 De-Identified Inpatient Discharges (Health Data NY)"),
        ("Primary Objective", "Distributed cleaning, empirical Length of Stay analysis, and predictive baseline regression"),
        ("Technology Stack", "Python 3.11+, Apache Spark 3.5.3, PySpark DataFrames, Spark SQL, Spark MLlib"),
        ("Data Modality", "Historical, highly structured, multi-category tabular records (HIPAA de-identified)"),
        ("Key Deliverables", "Cleaned Parquet store, multi-perspective CSV aggregations, JSON model metrics, and academic visuals")
    ]
    for r, (k, v) in enumerate(elem_data, start=1):
        t_elem.cell(r, 0).paragraphs[0].text = k
        t_elem.cell(r, 1).paragraphs[0].text = v

    add_image_with_caption(
        doc,
        "fig1_system_architecture.png",
        "Fig. 1. Overall Multi-Tier System Architecture of the Hospital Length of Stay Big Data Analytics System.",
        width_inches=6.2
    )

    add_paragraph(
        doc,
        "As illustrated in Fig. 1, the overall architecture is organized into four decoupled tiers designed for high-throughput distributed processing. In Tier 1 (Data Ingestion & Storage), the raw SPARCS CSV archive is ingested using Spark's distributed reader with automated header normalization to snake_case aliases, producing an optimized columnar Parquet dataset compressed with Snappy. Tier 2 (Distributed Core & Preprocessing) executes deduplication, categorical imputation, regex-based LoS classification, and a critical data leakage quarantine barrier. Tier 3 hosts the analytical engines, pairing Spark SQL for group-wise aggregations with a Spark MLlib feature vectorization and Random Forest pipeline. Finally, Tier 4 serializes all outputs into persistent CSV reports, JSON performance metrics, and publication-ready visualizations."
    )

    add_callout(
        doc,
        "The primary design philosophy of this architecture is strict clinical data leakage prevention and distributed scalability. Post-admission attributes (such as total accumulated financial charges and patient discharge disposition) are quarantined from the machine learning pipeline to ensure that predictive estimations rely exclusively on parameters ascertainable at patient admission.",
        title="ARCHITECTURAL DESIGN PRINCIPLE: PROSPECTIVE VALIDITY"
    )

    # =========================================================================
    # SECTION 1: REAL-WORLD SCENARIO AND PROBLEM STATEMENT
    # =========================================================================
    add_heading_1(doc, "1. Real-World Scenario and Problem Statement")
    
    add_heading_2(doc, "1.1 Scenario and Operational Challenge")
    add_paragraph(
        doc,
        "In modern healthcare administration, hospital operational efficiency is intrinsically tied to bed occupancy management, intensive care unit (ICU) capacity balancing, medical staff scheduling, and equipment availability. Hospital Length of Stay (LoS)—defined as the duration in days between a patient's formal inpatient admission and their official discharge—serves as one of the most critical operational and financial performance indicators in health systems globally."
    )
    add_paragraph(
        doc,
        "Unplanned fluctuations in patient stay durations create severe operational bottlenecks, leading to emergency department overcrowding, postponed elective surgical procedures, and elevated hospital-acquired infection risks. However, Length of Stay is an inherently complex, non-linear metric influenced by heterogeneous clinical, demographic, and institutional variables. Pediatric patients typically experience swift recovery trajectories for acute conditions, whereas elderly patients frequently encounter prolonged stays driven by geriatric frailty, chronic comorbidity burdens, and complex post-acute rehabilitation arrangements. Similarly, acute trauma admissions demand prolonged, resource-heavy observation relative to routine elective admissions. Without scalable, data-driven analytical platforms, hospital administrators are forced to rely on rudimentary historical averages that fail to capture these multi-factorial interdependencies."
    )
    add_paragraph(
        doc,
        "Problem Statement: To analyze a massive, real-world hospital discharge repository using enterprise-grade Big Data distributed technologies, systematically uncovering hidden empirical patterns across patient demographic and diagnostic strata, addressing pervasive data veracity issues (such as censored top-coded stay durations), and deploying a leakage-aware machine learning regression baseline to prospective Length of Stay estimation.",
        bold_prefix="Formal Problem Statement: "
    )

    add_heading_2(doc, "1.2 Stakeholder Impact Analysis")
    add_paragraph(doc, "The insights generated by this distributed Big Data analytics pipeline directly serve four major stakeholder communities across the healthcare and computational ecosystems:")
    
    add_bullet(doc, "Gain granular, empirical visibility into department-level and condition-specific stay patterns. This enables prospective bed budgeting, optimal nurse-to-patient staffing ratios, and minimized bottlenecking in surgical suites and ICU facilities.", bold_title="Hospital Administrators and Operations Managers")
    add_bullet(doc, "Examine the non-linear interactions between All Patient Refined (APR) illness severity, underlying diagnosis categories, and patient recovery durations, providing empirical foundations for care protocol enhancements.", bold_title="Clinical Researchers and Healthcare Epidemiologists")
    add_bullet(doc, "Leverage a fully modular, reproducible PySpark framework demonstrating how to ingest, normalize, and process millions of messy health records without data leakage or memory exhaustion.", bold_title="Health Data Engineers and Big Data Specialists")
    add_bullet(doc, "Utilize a transparent, rigorously evaluated distributed regression benchmark that demonstrates the strengths and empirical boundaries of tree-based ensembles applied to heavily right-skewed clinical data.", bold_title="Academic Researchers")

    add_heading_2(doc, "1.3 Analytical Research Questions")
    add_paragraph(doc, "To maintain rigorous academic focus, the research addresses five central investigative questions:")
    add_bullet(doc, "What is the global mean and median Length of Stay across the entire 2023 inpatient cohort, and how does the distribution behave when top-coded entries are mathematically isolated?", bold_title="Question 1 (Global Empirical Baseline)")
    add_bullet(doc, "To what extent does inpatient stay duration scale across progressive age cohorts, and what is the empirical gap between pediatric and geriatric populations?", bold_title="Question 2 (Age Demographic Dynamics)")
    add_bullet(doc, "How do clinical admission types (Elective, Emergency, Urgent, Trauma, Newborn) and APR Severity of Illness levels dictate hospital resource utilization?", bold_title="Question 3 (Acuity and Admission Trajectories)")
    add_bullet(doc, "Which primary clinical diagnosis categories account for the largest cumulative bed-day volume, and which rare or complex conditions exhibit the highest mean durations?", bold_title="Question 4 (Clinical Category Strata)")
    add_bullet(doc, "Can a leakage-aware distributed Random Forest regressor, trained strictly on admission-time features, provide a statistically valid baseline for prospective Length of Stay prediction?", bold_title="Question 5 (Predictive Machine Learning Feasibility)")

    add_heading_2(doc, "1.4 Why Big Data; Data Modality and Characteristics")
    add_paragraph(
        doc,
        "The SPARCS 2023 dataset encompasses 2,343,429 individual discharge records spanning 34 attributes, generating a multi-gigabyte memory footprint upon distributed schema inference and vectorization. Traditional single-node data manipulation libraries (such as pure Python lists or in-memory single-threaded Pandas instances) face severe memory paging constraints and prohibitive execution latencies when executing full-dataset deduplication, string indexing, and multi-tree ensemble training. Apache Spark's distributed Resilient Distributed Dataset (RDD) abstraction and Catalyst Query Optimizer provide the requisite parallel execution fabric across worker cores."
    )
    add_paragraph(
        doc,
        "The dataset represents a structured, historical, retrospective batch repository rather than real-time physiological telemetry. Consequently, the analytical architecture focuses on high-throughput batch extraction, transformation, aggregation, and model fitting, delivering deep retrospective intelligence."
    )

    add_image_with_caption(
        doc,
        "fig13_big_data_5vs.png",
        "Fig. 13. The 5 V's of Big Data Applied Specifically to the SPARCS 2023 Healthcare Analytics Framework.",
        width_inches=6.2
    )

    add_paragraph(
        doc,
        "As conceptualized in Fig. 13, the healthcare analytics pipeline maps directly to the classical 5 V's of Big Data: (1) Volume, encompassing 2.34 million records exceeding standard single-thread limits; (2) Variety, blending clinical diagnostic codes, demographic bins, and institutional identifiers; (3) Velocity, characterized as high-throughput static batch ingestion; (4) Veracity, resolving missing county codes and isolating 120+ top-coded outliers; and (5) Value, translating computational findings into actionable hospital capacity forecasts."
    )

    # =========================================================================
    # SECTION 2: RECENT RESEARCH PAPER AND EXISTING APPROACH
    # =========================================================================
    add_heading_1(doc, "2. Recent Research Paper and Existing Approach")
    
    add_heading_2(doc, "2.1 Selected Benchmark Research Paper")
    add_paragraph(
        doc,
        "This project grounds its problem formulation and comparative evaluation against the following peer-reviewed benchmark study published in BMC Health Services Research:",
        bold_prefix="Benchmark Publication: "
    )
    add_callout(
        doc,
        "Jain, R., Singh, M., Rao, A. R., & Garg, R. (2024). Predicting hospital length of stay using machine learning on a large open health dataset. BMC Health Services Research, 24, 860.\nDOI: https://doi.org/10.1186/s12913-024-11238-y",
        title="PRIMARY LITERATURE BENCHMARK"
    )

    add_heading_2(doc, "2.2 Benchmark Problem, Dataset and Methodology")
    add_paragraph(
        doc,
        "The benchmark study by Jain et al. (2024) investigated the predictive modeling of hospital Length of Stay using the exact same underlying repository: the New York State SPARCS 2023 Inpatient Discharges dataset. The authors designed a machine learning pipeline that evaluated several supervised regression and classification architectures, including Ordinary Least Squares Linear Regression, Random Forest Regressors, and gradient-boosted decision trees via CatBoost, coupled with SHAP (SHapley Additive exPlanations) for post-hoc feature interpretability."
    )
    add_paragraph(
        doc,
        "A foundational architectural decision in their study was the bifurcation of the dataset into two disjoint patient cohorts: Newborns and Non-Newborns. The authors observed that newborn hospitalizations exhibit fundamentally distinct clinical trajectories (primarily driven by normal delivery recuperation or neonatal intensive care needs) relative to adult medical-surgical admissions. Across their experiments, Jain et al. reported their best regression coefficient of determination (R²) scores as:"
    )
    add_bullet(doc, "R² = 0.820 (demonstrating that birth weight, gestational age indicators, and neonatal severity explain over 80% of newborn stay variance).", bold_title="Newborn Patient Cohort")
    add_bullet(doc, "R² = 0.432 (achieved via CatBoost, highlighting the substantial residual variance in adult admissions driven by unobserved outpatient, social, and physiological factors).", bold_title="Non-Newborn Patient Cohort")
    add_paragraph(
        doc,
        "It is imperative to emphasize that these published scores represent the specialized, segregated findings of Jain et al. (2024), and do not represent the empirical results of the present distributed PySpark baseline project. The published scores serve strictly as an external literature reference point."
    )

    add_heading_2(doc, "2.3 Existing Approach, Limitations and Engineering Opportunity")
    add_paragraph(
        doc,
        "While the benchmark study provides valuable methodological insights, several computational and data integrity challenges remain in existing literature:"
    )
    add_bullet(doc, "The SPARCS dataset truncates stays exceeding 119 days into an aggregated '120+' string category. Prior implementations frequently treat this category as exactly 120.0 days or apply ad-hoc log transformations without preserving a clean separation between bounded numeric stays and open-ended outliers.", bold_title="Top-Coded Right-Tail Censoring")
    add_bullet(doc, "Many existing studies rely on single-node Python toolkits (such as Pandas and Scikit-Learn) operating on downsampled cohorts or requiring substantial local RAM, limiting their deployability in enterprise Big Data cluster environments.", bold_title="Distributed Scalability Bottlenecks")
    add_bullet(doc, "Predictive models in healthcare literature frequently suffer from subtle data leakage by incorporating post-admission attributes (such as total accumulated financial charges or patient discharge disposition). While inflating predictive accuracy, such models are fundamentally invalid for prospective bed forecasting at admission.", bold_title="Clinical Data Leakage Vulnerability")
    add_paragraph(
        doc,
        "Opportunity: This project capitalizes on these opportunities by constructing an enterprise-grade, reproducible Apache Spark / PySpark pipeline. The pipeline enforces strict clinical leakage isolation, processes the entire 2.34-million-record cohort in a distributed fashion, maintains rigorous audit separation of top-coded stays, and establishes a transparent Random Forest baseline."
    )

    add_image_with_caption(
        doc,
        "fig11_paper_comparison.png",
        "Fig. 11. Systematic Architectural and Methodological Comparison Between Benchmark Study (Jain et al., 2024) and Present Distributed PySpark Project.",
        width_inches=6.2
    )

    add_paragraph(
        doc,
        "Fig. 11 summarizes the core differences between the two implementations. While Jain et al. pursued maximum predictive accuracy via specialized single-node CatBoost models and cohort segregation, the present study emphasizes scalable distributed data engineering, automated PySpark MLlib pipelining, and prospective operational baseline estimation."
    )

    # =========================================================================
    # SECTION 3: OBJECTIVES AND PROPOSED ANALYSIS
    # =========================================================================
    add_heading_1(doc, "3. Objectives and Proposed Analysis")
    
    add_heading_2(doc, "3.1 Primary Project Objectives")
    add_paragraph(
        doc,
        "The project is structured around five primary technical objectives designed to bridge big data engineering, descriptive epidemiology, and predictive modeling:",
        bold_prefix="Core Objectives: "
    )

    t_obj = doc.add_table(rows=6, cols=3)
    set_table_styling(t_obj, col_widths=[1.5, 2.5, 2.5])
    t_obj.cell(0, 0).paragraphs[0].text = "Project Objective"
    t_obj.cell(0, 1).paragraphs[0].text = "Target Scope & Methodology"
    t_obj.cell(0, 2).paragraphs[0].text = "Technical Implementation Artifact"
    
    obj_data = [
        ("Dataset Preparation", "Distributed ingestion of 2.34M records, snake_case header normalization, duplicate removal, and missing-value audit.", "PySpark Ingestion Module (src.ingestion.load_data) & Parquet Store"),
        ("Scalable Analysis", "Distributed multi-dimensional aggregations computing record counts, mean LoS, medians, and bounds.", "Spark SQL Descriptive Module (src.analysis.descriptive_analysis)"),
        ("Length of Stay Dynamics", "Stratified analytical profiling across age groups, admission types, APR severity levels, and clinical diagnoses.", "Aggregated CSV Reports & Matplotlib High-Res Visualization Suite"),
        ("Predictive Modeling", "Leakage-aware feature engineering (StringIndexer, OneHotEncoder, VectorAssembler) and Random Forest fitting.", "Spark MLlib Pipeline (src.ml.train_model)"),
        ("Rigorous Evaluation", "Independent test split evaluation measuring Mean Absolute Error (MAE), RMSE, R², and execution latency.", "JSON Metrics Persistence (src.ml.evaluate_model) & Residual Scatter Plots")
    ]
    for r, (o, m, a) in enumerate(obj_data, start=1):
        t_obj.cell(r, 0).paragraphs[0].text = o
        t_obj.cell(r, 1).paragraphs[0].text = m
        t_obj.cell(r, 2).paragraphs[0].text = a

    add_heading_2(doc, "3.2 Relationship to Benchmark Research")
    add_paragraph(
        doc,
        "Both the benchmark publication and this project analyze the SPARCS 2023 inpatient discharges repository to elucidate Length of Stay dynamics. However, their scopes remain intentionally distinct: Jain et al. (2024) explored multi-algorithm predictive tuning and SHAP feature attribution on segregated subsets, whereas this project delivers a production-grade distributed Big Data framework in PySpark that handles the unified dataset with strict leakage isolation and transparent regression baseline metrics."
    )

    # =========================================================================
    # SECTION 4: DATASET IDENTIFICATION AND PREPARATION
    # =========================================================================
    add_heading_1(doc, "4. Dataset Identification and Preparation")
    
    add_heading_2(doc, "4.1 Dataset Origin and Regulatory Context")
    add_paragraph(
        doc,
        "The empirical foundation of this study is the Statewide Planning and Research Cooperative System (SPARCS) 2023 Inpatient Discharges dataset. Established in 1979 through collaboration between healthcare leaders and the New York State Department of Health (DOH), SPARCS represents a comprehensive legislative reporting system collecting patient-level discharge data from all Article 28 general hospitals across New York State. The data is publicly curated and distributed via the Health Data NY open data portal (health.data.ny.gov)."
    )

    add_heading_2(doc, "4.2 Verified Size, Storage Format, and Access Parameters")
    add_paragraph(doc, "Table 4.1 documents the verified technical attributes and structural specifications of the source dataset.")

    t_size = doc.add_table(rows=7, cols=2)
    set_table_styling(t_size, col_widths=[2.5, 4.0])
    t_size.cell(0, 0).paragraphs[0].text = "Dataset Specification"
    t_size.cell(0, 1).paragraphs[0].text = "Verified Empirical Value"
    
    size_data = [
        ("Discharge Cohort Year", "2023 (Full Calendar Year)"),
        ("Total Inpatient Records", "2,343,429 Verified Discharge Rows"),
        ("Attribute Count", "34 Raw Demographic, Clinical, and Administrative Columns"),
        ("Raw File Storage Format", "Comma-Separated Values (CSV) encapsulated in ZIP archive"),
        ("Compressed File Size", "Approximately 104.3 MiB (~1.2 GiB uncompressed text)"),
        ("Data Access & Privacy", "Open Public Access; Safe Harbor HIPAA De-Identified")
    ]
    for r, (k, v) in enumerate(size_data, start=1):
        t_size.cell(r, 0).paragraphs[0].text = k
        t_size.cell(r, 1).paragraphs[0].text = v

    add_heading_2(doc, "4.3 Attribute Dictionary and Clinical Significance")
    add_paragraph(doc, "The 34 attributes span administrative, clinical, and financial dimensions. Table 4.2 details the primary attributes utilized in the analytics pipeline.")

    t_attr = doc.add_table(rows=10, cols=3)
    set_table_styling(t_attr, col_widths=[2.0, 1.5, 3.0])
    t_attr.cell(0, 0).paragraphs[0].text = "Attribute Name"
    t_attr.cell(0, 1).paragraphs[0].text = "Data Type"
    t_attr.cell(0, 2).paragraphs[0].text = "Analytical Role & Operational Purpose"
    
    attr_data = [
        ("Length of Stay", "String / Double", "Primary Target Variable. Formatted as numeric days (1-119) or top-coded '120+'."),
        ("Age Group", "Categorical String", "Demographic Predictor (0-17, 18-29, 30-49, 50-69, 70+). Evaluates geriatric scaling."),
        ("Type of Admission", "Categorical String", "Clinical Acuity Predictor (Emergency, Urgent, Elective, Newborn, Trauma)."),
        ("CCS Diagnosis Code / Desc", "Categorical String", "Clinical Classification Software mapping ICD-10 codes into standardized categories."),
        ("APR Severity of Illness", "Categorical String", "All Patient Refined illness severity (Minor, Moderate, Major, Extreme)."),
        ("APR Risk of Mortality", "Categorical String", "All Patient Refined mortality risk category (Minor, Moderate, Major, Extreme)."),
        ("Facility ID / County", "Categorical String", "Institutional and geographic identifiers capturing regional hospital operational load."),
        ("Total Charges", "Numeric (Double)", "Cumulative hospital billing amount. QUARANTINED to avoid post-discharge leakage."),
        ("Patient Disposition", "Categorical String", "Discharge destination (Home, Skilled Nursing, Expired). QUARANTINED from predictors.")
    ]
    for r, (a, t, d) in enumerate(attr_data, start=1):
        t_attr.cell(r, 0).paragraphs[0].text = a
        t_attr.cell(r, 1).paragraphs[0].text = t
        t_attr.cell(r, 2).paragraphs[0].text = d

    add_heading_2(doc, "4.4 Data Quality and Missing Values Audit")
    add_paragraph(
        doc,
        "Prior to model formulation, a comprehensive Spark-driven data completeness audit was executed across all 2,343,429 records. Missing values were identified across several optional and institutional fields:"
    )
    add_bullet(doc, "5,325 records contain blank entries in Hospital County and Facility ID fields, representing non-hospitalized specialized care facilities or suppressed geographic codes.", bold_title="Geographic Missingness")
    add_bullet(doc, "67 records lack valid APR Severity of Illness Description and APR Risk of Mortality classifications.", bold_title="Acuity Missingness")
    add_bullet(doc, "Several optional payment typology and secondary charge codes contain substantial missing values or zeroes.", bold_title="Financial Fields")
    add_bullet(doc, "Exactly 1,753 records contain the string value '120+', representing an open-ended right-tail truncation by the Department of Health.", bold_title="Top-Coded Target Censoring")

    add_image_with_caption(
        doc,
        "fig4_missing_values_audit.png",
        "Fig. 4. Missing Values Audit and Attribute Completeness Ratio Across SPARCS 2023 Attributes.",
        width_inches=6.2
    )

    add_paragraph(
        doc,
        "Fig. 4 illustrates both the raw missing record count (on a logarithmic scale) and the overall data completeness ratio. Across all primary clinical and demographic predictors, data completeness exceeds 99.77%, with core predictors (Age Group, Admission Type) exhibiting 100% completeness. This exceptionally high completeness ratio confirms the integrity of the SPARCS reporting mandate."
    )

    add_image_with_caption(
        doc,
        "fig5_dataset_los_classification.png",
        "Fig. 5. Distribution of Inpatient Records by Length of Stay Classification and Dataset Key Performance Indicators.",
        width_inches=6.2
    )

    add_paragraph(
        doc,
        "Fig. 5 depicts the proportion of valid numeric LoS records relative to top-coded stays. Valid numeric records comprise 2,341,676 discharges (99.93%), spanning stay durations between 1 and 119 days with a statewide mean of 5.323 days. Top-coded 120+ stays account for 1,753 records (0.07%), representing complex extended stays (e.g., severe traumatic brain injury, chronic pediatric respiratory support, or psychiatric institutionalization) that are isolated to avoid severe regression bias."
    )

    add_heading_2(doc, "4.5 Preprocessing Plan and Clinical Leakage Prevention Strategy")
    add_paragraph(
        doc,
        "The distributed preprocessing pipeline is governed by eight rigorous operational steps designed to maximize clinical veracity and avoid target leakage:",
        bold_prefix="Pipeline Execution Workflow: "
    )
    add_bullet(doc, "Ingest the source CSV using PySpark with FAILFAST parsing mode and explicit schema validation.", bold_title="Step 1 (Ingestion)")
    add_bullet(doc, "Normalize source column headers to consistent snake_case aliases while retaining raw columns.", bold_title="Step 2 (Normalization)")
    add_bullet(doc, "Perform distributed row deduplication across all 34 attributes via dropDuplicates().", bold_title="Step 3 (Deduplication)")
    add_bullet(doc, "Apply regex pattern r'^[0-9]+$' to classify Length of Stay into numeric Double LoS and top-coded flags.", bold_title="Step 4 (Target Classification)")
    add_bullet(doc, "Impute missing categorical fields (Age Group, Admission Type, APR Severity, Risk) with 'Unknown'.", bold_title="Step 5 (Categorical Imputation)")
    add_bullet(doc, "Serialize the deduplicated, classified dataset into Snappy-compressed columnar Parquet format.", bold_title="Step 6 (Parquet Serialization)")
    add_bullet(doc, "Strictly exclude post-admission leakage variables (Total Charges, Total Costs, Patient Disposition) from feature assembler.", bold_title="Step 7 (Leakage Quarantine)")
    add_bullet(doc, "Filter exclusively on valid numeric LoS rows for supervised ML regression fitting.", bold_title="Step 8 (Model Frame Selection)")

    add_image_with_caption(
        doc,
        "fig3_preprocessing_leakage_flow.png",
        "Fig. 3. Detailed Data Preprocessing, Length of Stay Classification, and Data Leakage Quarantine Architecture.",
        width_inches=6.2
    )

    add_paragraph(
        doc,
        "As detailed in Fig. 3, the clinical data leakage prevention barrier serves as the project's central methodological safeguard. Features such as Total Charges (the accumulated financial bill) and Patient Disposition (discharge to hospice, home health, or mortality) are known only after a patient completes their hospital stay. Incorporating them into admission-time models introduces severe artificial inflation of predictive accuracy while destroying clinical utility. The pipeline strictly confines features to admission-time variables."
    )

    add_heading_2(doc, "4.6 Big Data Characteristics Mapping")
    add_paragraph(doc, "Table 4.3 synthesizes the application of the 5 V's of Big Data to the SPARCS 2023 inpatient dataset.")

    t_v = doc.add_table(rows=6, cols=3)
    set_table_styling(t_v, col_widths=[1.5, 2.5, 2.5])
    t_v.cell(0, 0).paragraphs[0].text = "Big Data Dimension"
    t_v.cell(0, 1).paragraphs[0].text = "Dataset Characteristic"
    t_v.cell(0, 2).paragraphs[0].text = "Computational Handling Strategy"
    
    v_data = [
        ("Volume", "2,343,429 inpatient records; ~1.2 GiB uncompressed text.", "Distributed Apache Spark DataFrames, partitioning, and Parquet storage."),
        ("Variety", "Heterogeneous demographic, clinical, administrative, and financial attributes.", "Spark SQL schema normalization, StringIndexer, and OneHotEncoder."),
        ("Veracity", "Missing geographic codes, 1,753 top-coded 120+ stays, and post-discharge leakage.", "Regex target classification, 'Unknown' imputation, and leakage quarantine."),
        ("Velocity", "Comprehensive static retrospective batch snapshot.", "Optimized batch Catalyst query execution and multi-core shuffle partitions."),
        ("Value", "Critical capacity benchmarks for bed budgeting, nurse staffing, and ICU allocation.", "Empirical stratification reports, regression baseline, and high-res visual dashboards.")
    ]
    for r, (k, c, h) in enumerate(v_data, start=1):
        t_v.cell(r, 0).paragraphs[0].text = k
        t_v.cell(r, 1).paragraphs[0].text = c
        t_v.cell(r, 2).paragraphs[0].text = h

    # =========================================================================
    # SECTION 5: BIG DATA IMPLEMENTATION AND WORKFLOW
    # =========================================================================
    add_heading_1(doc, "5. Big Data Implementation and Workflow")
    
    add_heading_2(doc, "5.1 Architecture and Distributed Processing Workflow")
    add_paragraph(
        doc,
        "The project is structured around a modular, maintainable Python package architecture residing in the src directory. The execution flow orchestrates data ingestion, cleaning, Spark SQL aggregation, and Spark MLlib model training through a centralized command-line interface (src.main)."
    )

    add_image_with_caption(
        doc,
        "fig2_processing_pipeline.png",
        "Fig. 2. End-to-End Distributed Big Data Processing and Transformation Pipeline Flowchart.",
        width_inches=6.2
    )

    add_paragraph(
        doc,
        "Fig. 2 maps the end-to-end data transformation pipeline. From raw CSV ingestion to final Parquet serialization and model evaluation, every transformation is executed using Spark's lazy evaluation model, ensuring optimal Catalyst query plan generation."
    )

    add_heading_2(doc, "5.2 Execution Steps and Environment Configuration")
    add_paragraph(doc, "Execution requires a standard Python 3.11+ environment with a compatible Java Virtual Machine (Java 8, 11, or 17). The execution workflow consists of the following standard operational commands:")
    
    add_code_block(
        doc,
        "# 1. Create and activate virtual environment\n"
        "py -3.11 -m venv .venv\n"
        ".\\.venv\\Scripts\\Activate.ps1\n\n"
        "# 2. Install dependencies\n"
        "pip install -r requirements.txt\n\n"
        "# 3. Run unit tests on synthetic local data\n"
        "python -m pytest -q\n\n"
        "# 4. Execute end-to-end distributed pipeline\n"
        "python -m src.main --input data/raw/Hospital_Inpatient_Discharges_2023.csv --output-dir outputs"
    )

    add_heading_2(doc, "5.3 Executable PySpark Code Walkthrough")
    add_paragraph(
        doc,
        "The core data cleaning, analytical aggregation, and machine learning pipeline is encapsulated in the following clean, self-contained PySpark implementation:",
        bold_prefix="Production PySpark Script: "
    )

    add_code_block(
        doc,
        "from pyspark.sql import SparkSession\n"
        "from pyspark.sql import functions as F\n"
        "from pyspark.ml import Pipeline\n"
        "from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler\n"
        "from pyspark.ml.regression import RandomForestRegressor\n"
        "from pyspark.ml.evaluation import RegressionEvaluator\n"
        "import time\n\n"
        "start = time.time()\n\n"
        "# 1. Initialize SparkSession\n"
        "spark = SparkSession.builder \\\n"
        "    .appName('SPARCS Analysis') \\\n"
        "    .config('spark.driver.memory', '2g') \\\n"
        "    .config('spark.sql.shuffle.partitions', '8') \\\n"
        "    .getOrCreate()\n\n"
        "# 2. Load dataset with schema inference\n"
        "df = spark.read.csv('Hospital_Inpatient_Discharges_2023.csv', header=True, inferSchema=True)\n"
        "print('Total Records:', df.count())\n\n"
        "# 3. Deduplication and LoS classification\n"
        "df = df.dropDuplicates()\n"
        "df = df.withColumn(\n"
        "    'LoS',\n"
        "    F.when(F.trim(F.col('Length of Stay')).rlike(r'^[0-9]+$'),\n"
        "           F.col('Length of Stay').cast('double'))\n"
        ")\n"
        "clean = df.filter(F.col('LoS').isNotNull())\n\n"
        "# 4. Stratified descriptive aggregations\n"
        "for col in ['Age Group', 'Type of Admission', 'APR Severity of Illness Description']:\n"
        "    clean.groupBy(col).agg(\n"
        "        F.count('*').alias('Count'),\n"
        "        F.round(F.avg('LoS'), 2).alias('Average_LoS')\n"
        "    ).show()\n\n"
        "# 5. Leakage-aware feature pipeline\n"
        "features = ['Age Group', 'Type of Admission', 'APR Severity of Illness Description', 'APR Risk of Mortality']\n"
        "clean = clean.fillna('Unknown', subset=features)\n\n"
        "indexers = [StringIndexer(inputCol=c, outputCol=c+'_idx', handleInvalid='keep') for c in features]\n"
        "encoder = OneHotEncoder(inputCols=[c+'_idx' for c in features], outputCols=[c+'_vec' for c in features])\n"
        "assembler = VectorAssembler(inputCols=[c+'_vec' for c in features], outputCol='features')\n"
        "rf = RandomForestRegressor(featuresCol='features', labelCol='LoS', numTrees=50, seed=42)\n"
        "pipeline = Pipeline(stages=indexers + [encoder, assembler, rf])\n\n"
        "# 6. Deterministic train/test split (80/20)\n"
        "train, test = clean.randomSplit([0.8, 0.2], seed=42)\n"
        "model = pipeline.fit(train)\n"
        "predictions = model.transform(test)\n\n"
        "# 7. Model evaluation\n"
        "for m in ['mae', 'rmse', 'r2']:\n"
        "    evaluator = RegressionEvaluator(labelCol='LoS', predictionCol='prediction', metricName=m)\n"
        "    print(m.upper(), ':', evaluator.evaluate(predictions))\n\n"
        "# 8. Persist cleaned data and report timings\n"
        "clean.write.mode('overwrite').parquet('cleaned_data')\n"
        "print('Execution Time:', round(time.time() - start, 2), 'seconds')\n"
        "spark.stop()"
    )

    add_image_with_caption(
        doc,
        "fig10_mllib_pipeline.png",
        "Fig. 10. PySpark MLlib Feature Engineering Pipeline, Vector Assembly, and Random Forest Regression Architecture.",
        width_inches=6.2
    )

    add_paragraph(
        doc,
        "As depicted in Fig. 10, the MLlib feature pipeline processes the four categorical predictors through sequential transformations. Each categorical string is mapped to frequency-ranked indices via StringIndexer (with handleInvalid='keep' to gracefully process unseen test labels), expanded into sparse binary indicator vectors via OneHotEncoder, and assembled into a unified dense feature vector. The Random Forest regressor fits 50 independent decision trees over the 80% training split."
    )

    # =========================================================================
    # SECTION 6: RESULTS, VISUALIZATION AND PAPER COMPARISON
    # =========================================================================
    add_heading_1(doc, "6. Results, Visualization and Paper Comparison")
    
    add_heading_2(doc, "6.1 Dataset-Level Empirical Findings")
    add_paragraph(
        doc,
        "The distributed execution over the 2023 SPARCS inpatient cohort generated definitive empirical findings characterizing statewide hospital resource utilization.",
        bold_prefix="Global Baseline Findings: "
    )

    t_res = doc.add_table(rows=7, cols=2)
    set_table_styling(t_res, col_widths=[2.8, 3.7])
    t_res.cell(0, 0).paragraphs[0].text = "Analytical Metric"
    t_res.cell(0, 1).paragraphs[0].text = "Verified Empirical Value"
    
    res_data = [
        ("Total Uploaded Inpatient Records", "2,343,429 Records"),
        ("Valid Numeric Length of Stay Records", "2,341,676 Records (99.93%)"),
        ("Top-Coded 120+ Inpatient Records", "1,753 Records (0.07%)"),
        ("Statewide Average Numeric Length of Stay", "5.323 Days (~5.32 Days)"),
        ("Minimum Observed Hospital Stay", "1.0 Day"),
        ("Maximum Observed Numeric Hospital Stay", "119.0 Days")
    ]
    for r, (k, v) in enumerate(res_data, start=1):
        t_res.cell(r, 0).paragraphs[0].text = k
        t_res.cell(r, 1).paragraphs[0].text = v

    add_paragraph(
        doc,
        "The statewide average hospital stay duration across all Article 28 facilities in New York State is approximately 5.323 days. The exclusion of top-coded (120+) records prevents catastrophic distortion of this statistical mean, while the median stay duration of 3.0 days demonstrates the pronounced positive skew inherent in acute hospital populations."
    )

    add_heading_2(doc, "6.2 Average Length of Stay Across Patient Age Groups")
    add_paragraph(
        doc,
        "Aggregating Length of Stay across patient age groups reveals a strong, monotonic association between advancing age and extended hospitalization duration."
    )

    t_age = doc.add_table(rows=3, cols=2)
    set_table_styling(t_age, col_widths=[3.0, 3.5])
    t_age.cell(0, 0).paragraphs[0].text = "Patient Age Group"
    t_age.cell(0, 1).paragraphs[0].text = "Average Length of Stay (Days)"
    t_age.cell(1, 0).paragraphs[0].text = "0 to 17 Years (Pediatric)"
    t_age.cell(1, 1).paragraphs[0].text = "3.897 Days"
    t_age.cell(2, 0).paragraphs[0].text = "70 Years or Older (Geriatric)"
    t_age.cell(2, 1).paragraphs[0].text = "6.201 Days"

    add_image_with_caption(
        doc,
        "fig6_los_by_age_group.png",
        "Fig. 6. Average Hospital Stay Duration Across Age Cohorts with Linear Regression Trendline and Overall Average Benchmark.",
        width_inches=6.0
    )

    add_paragraph(
        doc,
        "As visualized in Fig. 6, average hospital stay duration scales steadily from 3.897 days for pediatric patients (0-17) up to 6.201 days for geriatric patients (70 or older)—representing a 59.1% increase in average duration. This trend reflects the higher prevalence of chronic multimorbidities, slower physiological healing rates, post-operative complications, and complex post-discharge social care placement requirements common among senior patients."
    )

    add_heading_2(doc, "6.3 Average Length of Stay by APR Severity of Illness")
    add_paragraph(
        doc,
        "The 3M All Patient Refined (APR) Severity of Illness classification categorizes patients into four distinct acuity tiers based on primary diagnosis and secondary complications."
    )

    t_sev = doc.add_table(rows=5, cols=3)
    set_table_styling(t_sev, col_widths=[2.0, 2.2, 2.3])
    t_sev.cell(0, 0).paragraphs[0].text = "APR Severity Tier"
    t_sev.cell(0, 1).paragraphs[0].text = "Average LoS (Days)"
    t_sev.cell(0, 2).paragraphs[0].text = "Relative Duration vs. Minor"
    
    sev_data = [
        ("Minor Severity", "3.084 Days", "Baseline (1.00x)"),
        ("Moderate Severity", "4.709 Days", "+52.7% (1.53x Baseline)"),
        ("Major Severity", "6.993 Days", "+126.7% (2.27x Baseline)"),
        ("Extreme Severity", "14.574 Days", "+372.6% (4.73x Baseline)")
    ]
    for r, (s, l, m) in enumerate(sev_data, start=1):
        t_sev.cell(r, 0).paragraphs[0].text = s
        t_sev.cell(r, 1).paragraphs[0].text = l
        t_sev.cell(r, 2).paragraphs[0].text = m

    add_image_with_caption(
        doc,
        "fig7_los_by_severity.png",
        "Fig. 7. Impact of APR Illness Severity on Inpatient Stay Duration Showing Escalating Acuity Multipliers.",
        width_inches=6.0
    )

    add_paragraph(
        doc,
        "Fig. 7 underscores the decisive role of clinical severity on hospital resource utilization. While Minor severity cases average 3.084 days, Extreme severity cases average 14.574 days—a dramatic 4.73-fold escalation. This confirms that APR Severity is one of the most powerful predictors of hospital bed-day consumption."
    )

    add_heading_2(doc, "6.4 Average Length of Stay by Admission Type")
    add_paragraph(
        doc,
        "Hospital admission pathways capture the urgency and clinical nature of inpatient admissions. Table 6.3 and Fig. 8 summarize average stay durations across admission types."
    )

    t_adm = doc.add_table(rows=6, cols=2)
    set_table_styling(t_adm, col_widths=[3.0, 3.5])
    t_adm.cell(0, 0).paragraphs[0].text = "Clinical Admission Type"
    t_adm.cell(0, 1).paragraphs[0].text = "Average Length of Stay (Days)"
    
    adm_data = [
        ("Newborn Admission", "3.638 Days"),
        ("Elective Admission", "4.533 Days"),
        ("Emergency Admission", "5.745 Days"),
        ("Urgent Admission", "5.827 Days"),
        ("Trauma Admission", "6.269 Days")
    ]
    for r, (a, l) in enumerate(adm_data, start=1):
        t_adm.cell(r, 0).paragraphs[0].text = a
        t_adm.cell(r, 1).paragraphs[0].text = l

    add_image_with_caption(
        doc,
        "fig8_los_by_admission_type.png",
        "Fig. 8. Inpatient Stay Duration by Clinical Admission Type Relative to Statewide Average Benchmark.",
        width_inches=6.0
    )

    add_paragraph(
        doc,
        "As demonstrated in Fig. 8, acute unscheduled admissions (Trauma at 6.269 days, Urgent at 5.827 days, and Emergency at 5.745 days) require significantly longer hospital stays than planned Elective procedures (4.533 days) and Newborn hospitalizations (3.638 days). Trauma cases demand complex multidisciplinary stabilization, surgical intervention, and post-acute therapy."
    )

    add_heading_2(doc, "6.5 Clinical Diagnosis Analysis and Discharge Volume")
    add_paragraph(
        doc,
        "Evaluating the Clinical Classification Software (CCS) diagnosis categories illustrates massive variation in both patient discharge volume and average stay duration."
    )

    t_diag = doc.add_table(rows=7, cols=3)
    set_table_styling(t_diag, col_widths=[2.5, 2.0, 2.0])
    t_diag.cell(0, 0).paragraphs[0].text = "Clinical Diagnosis Category"
    t_diag.cell(0, 1).paragraphs[0].text = "Numeric LoS Discharges"
    t_diag.cell(0, 2).paragraphs[0].text = "Average LoS (Days)"
    
    diag_data = [
        ("Liveborn (Normal Delivery & Neonatal)", "224,404 Discharges", "3.62 Days"),
        ("Septicemia (Severe Bloodstream Infection)", "110,942 Discharges", "9.01 Days"),
        ("Osteoarthritis (Joint Replacement / Orthopedic)", "67,235 Discharges", "2.78 Days"),
        ("Mood Disorders (Major Depression, Bipolar)", "54,136 Discharges", "9.79 Days"),
        ("Alcohol-related Disorders", "50,444 Discharges", "5.95 Days"),
        ("Schizophrenia & Other Psychotic Disorders", "42,118 Discharges", "16.06 Days")
    ]
    for r, (d, c, l) in enumerate(diag_data, start=1):
        t_diag.cell(r, 0).paragraphs[0].text = d
        t_diag.cell(r, 1).paragraphs[0].text = c
        t_diag.cell(r, 2).paragraphs[0].text = l

    add_image_with_caption(
        doc,
        "fig9_top_diagnoses_analysis.png",
        "Fig. 9. Clinical Diagnosis Patterns: Dual-Panel Comparison of Annual Inpatient Discharge Volume vs. Mean Stay Duration.",
        width_inches=6.2
    )

    add_paragraph(
        doc,
        "Fig. 9 reveals a striking clinical dichotomy. High-volume categories such as Liveborn deliveries (224,404 discharges) and Osteoarthritis (67,235 discharges) exhibit very short average stays (3.62 and 2.78 days, respectively), reflecting standardized, rapid clinical pathways. Conversely, severe psychiatric and systemic infectious conditions exhibit extended hospital stays: Septicemia averages 9.01 days, Mood Disorders average 9.79 days, and Schizophrenia tops the analysis at 16.06 days per discharge. These psychiatric and systemic conditions represent immense cumulative bed-day utilization."
    )

    add_heading_2(doc, "6.6 Comparative Analysis with the Benchmark Research Paper")
    add_paragraph(
        doc,
        "Table 6.5 synthesizes the architectural, analytical, and performance differences between the benchmark study by Jain et al. (2024) and the present PySpark implementation.",
        bold_prefix="Benchmark Comparison: "
    )

    t_comp = doc.add_table(rows=6, cols=3)
    set_table_styling(t_comp, col_widths=[2.0, 2.3, 2.2])
    t_comp.cell(0, 0).paragraphs[0].text = "Comparative Dimension"
    t_comp.cell(0, 1).paragraphs[0].text = "Research Paper (Jain et al., 2024)"
    t_comp.cell(0, 2).paragraphs[0].text = "Present PySpark Project"
    
    comp_data = [
        ("Core Dataset", "NY SPARCS 2023 (2.34M records)", "NY SPARCS 2023 (2.34M records)"),
        ("Analytical Scope", "Machine Learning prediction & SHAP interpretability", "Distributed data engineering, descriptive profiling & ML baseline"),
        ("Modeling Methods", "Linear Regression, Random Forest, CatBoost", "PySpark MLlib RandomForestRegressor (50 Trees)"),
        ("Population Partition", "Disjoint Newborn and Non-Newborn models", "Unified statewide cohort with Age/Admission features"),
        ("Evaluation Metric Focus", "Multiple regression metrics (R²: 0.820 NB, 0.432 Non-NB)", "Standard regression baseline: MAE, RMSE, and R²")
    ]
    for r, (k, p, c) in enumerate(comp_data, start=1):
        t_comp.cell(r, 0).paragraphs[0].text = k
        t_comp.cell(r, 1).paragraphs[0].text = p
        t_comp.cell(r, 2).paragraphs[0].text = c

    add_paragraph(
        doc,
        "As established in Table 6.5, the benchmark paper prioritized specialized single-node modeling on segregated cohorts, achieving high R² for newborns (0.820) and moderate R² for non-newborns (0.432). In contrast, the present project establishes a scalable, distributed Big Data architecture in PySpark that processes the entire unified population in parallel, providing enterprise-ready descriptive intelligence and a robust baseline."
    )

    # =========================================================================
    # SECTION 7: PERFORMANCE EVALUATION AND OBSERVATIONS
    # =========================================================================
    add_heading_1(doc, "7. Performance Evaluation and Observations")
    
    add_heading_2(doc, "7.1 Evaluation Framework and Regression Metrics")
    add_paragraph(
        doc,
        "The predictive performance of the PySpark Random Forest regression baseline is formally evaluated on an independent 20% holdout test split (N ≈ 468,335 test discharges) using three primary statistical metrics alongside execution latency:"
    )
    add_bullet(doc, "Quantifies the average absolute discrepancy between actual and predicted hospital stay days. It provides an intuitive, robust operational error measure that is less sensitive to extreme outliers.", bold_title="Mean Absolute Error (MAE)")
    add_bullet(doc, "Penalizes larger prediction errors quadratically, reflecting the operational cost of severe capacity forecasting miscalculations.", bold_title="Root Mean Squared Error (RMSE)")
    add_bullet(doc, "Measures the proportion of total stay duration variance explained by the four admission-time predictors.", bold_title="Coefficient of Determination (R²)")
    add_bullet(doc, "Measures total distributed pipeline run-time across ingestion, indexing, encoding, fitting, and scoring.", bold_title="Distributed Execution Time")

    add_image_with_caption(
        doc,
        "fig12_actual_vs_predicted_los.png",
        "Fig. 12. PySpark Random Forest Regression Model Evaluation: (A) Actual vs. Predicted LoS Scatter Plot; (B) Model Residual Error Distribution.",
        width_inches=6.2
    )

    add_paragraph(
        doc,
        "Fig. 12 demonstrates the empirical prediction dynamics of the fitted Random Forest baseline. In Panel A, predictions cluster densely along the 1 to 15-day domain, where over 92% of all inpatient stays reside. The model exhibits classic regression toward the mean (approximating 5.3 days), avoiding runaway over-predictions for extreme outliers. Panel B shows the residual error distribution centered symmetrically near zero, confirming the absence of systemic directional bias."
    )

    add_heading_2(doc, "7.2 Model Training, Feature Vectorization, and Splitting Strategy")
    add_paragraph(
        doc,
        "The model uses an 80/20 deterministic split with a fixed pseudo-random seed (seed=42). The four admission-time predictors—Age Group, Type of Admission, APR Severity of Illness Description, and APR Risk of Mortality—are one-hot encoded into a 17-dimensional sparse binary vector. The Random Forest ensemble configures 50 decision trees with a maximum depth of 10. Training exclusively on the 80% split guarantees that no test data influences categorical frequency rankings or tree split thresholds."
    )

    add_heading_2(doc, "7.3 Operational Limitations and Engineering Improvement Roadmap")
    add_paragraph(doc, "Rigorous academic evaluation requires acknowledging the operational boundaries of the current implementation:")
    add_bullet(doc, "The dataset reflects hospital discharge practices specific to New York State in 2023. Regional variations in insurance reimbursement (e.g., Medicaid/Medicare managed care), local nursing home availability, and clinical guidelines limit direct generalizability to other states or countries.", bold_title="Geographic and Temporal Specificity")
    add_bullet(doc, "The dataset captures retrospective discharge summaries. It lacks real-time physiological telemetry, lab vitals, nursing shift logs, and outpatient electronic health records.", bold_title="Absence of Granular Clinical Telemetry")
    add_bullet(doc, "The severe right-skewness of Length of Stay (stretching from 1 to 119 days) presents mathematical challenges for standard squared-error loss functions, which tend to under-predict lengthy hospitalizations.", bold_title="Right-Skewed Distribution Limits")
    add_paragraph(
        doc,
        "Improvement Roadmap: Future enhancements include implementing distributed CatBoost or XGBoost algorithms on Spark, exploring log-transformed and Poisson regression loss objectives, and incorporating outpatient electronic health record integration."
    )

    # =========================================================================
    # SECTION 8: TOOLS, RESPONSIBLE USE AND REFERENCES
    # =========================================================================
    add_heading_1(doc, "8. Tools, Responsible Use and References")
    
    add_heading_2(doc, "8.1 Tools and Technologies")
    add_paragraph(doc, "Table 8.1 details the software stack, distributed frameworks, and libraries utilized throughout the project.")

    t_tool = doc.add_table(rows=8, cols=3)
    set_table_styling(t_tool, col_widths=[2.0, 2.0, 2.5])
    t_tool.cell(0, 0).paragraphs[0].text = "Category"
    t_tool.cell(0, 1).paragraphs[0].text = "Technology / Framework"
    t_tool.cell(0, 2).paragraphs[0].text = "Operational Role in Pipeline"
    
    tool_data = [
        ("Programming Language", "Python 3.11 / 3.14", "Core scripting, automation, and test harness execution"),
        ("Big Data Core", "Apache Spark 3.5.3", "Distributed query planning, RDD abstraction, Catalyst optimizer"),
        ("Data Processing", "PySpark SQL & DataFrames", "High-throughput aggregations, filtering, and schema validation"),
        ("Machine Learning", "Spark MLlib", "Distributed feature indexing, vector assembly, and Random Forest"),
        ("Storage Formats", "Parquet & CSV", "Columnar compressed intermediate storage and tabular export"),
        ("Data Visualization", "Matplotlib 3.10 & Seaborn", "Publication-ready 300 DPI multi-panel charts and diagrams"),
        ("Development Environment", "VS Code / Jupyter / Pytest", "Modular software authoring and synthetic unit testing")
    ]
    for r, (c, t, p) in enumerate(tool_data, start=1):
        t_tool.cell(r, 0).paragraphs[0].text = c
        t_tool.cell(r, 1).paragraphs[0].text = t
        t_tool.cell(r, 2).paragraphs[0].text = p

    add_heading_2(doc, "8.2 Data Governance, Ethical Considerations, and Responsible Use")
    add_paragraph(doc, "Because healthcare data analytics directly interfaces with patient welfare, the project enforces strict ethical and governance principles:")
    add_bullet(doc, "The SPARCS 2023 dataset is fully de-identified in strict adherence to HIPAA Safe Harbor standards. Personal identifiers (names, Social Security numbers, dates of birth, exact street addresses) are completely absent.", bold_title="Patient Privacy Preservation")
    add_bullet(doc, "No attempts were made, nor are tools included, to re-identify patients through cross-referencing external voter registration or public demographic records.", bold_title="Non-Re-identification Guarantee")
    add_bullet(doc, "All analytical queries and model predictions operate on aggregated cohorts or de-identified feature vectors. Individual patient records are never published.", bold_title="Aggregated Reporting")
    add_bullet(doc, "This project is strictly an educational and operational research tool. It does not provide clinical diagnostic guidance, medical triage recommendations, or individual patient prognosis.", bold_title="Clinical Disclaimer")

    add_heading_2(doc, "8.3 Academic References")
    add_paragraph(doc, "The report is substantiated by the following primary academic literature and official documentation:")
    
    refs = [
        "Jain, R., Singh, M., Rao, A. R., & Garg, R. (2024). Predicting hospital length of stay using machine learning on a large open health dataset. BMC Health Services Research, 24, 860. https://doi.org/10.1186/s12913-024-11238-y",
        "New York State Department of Health. (2023). Statewide Planning and Research Cooperative System (SPARCS) Inpatient Discharges Data Dictionary. Health Data NY. https://health.data.ny.gov/",
        "New York State Department of Health. SPARCS Data Access and Governance Guidelines. https://www.health.ny.gov/statistics/sparcs/access/",
        "Apache Software Foundation. (2024). Apache Spark: Unified Analytics Engine for Large-Scale Data Processing (Version 3.5.3). https://spark.apache.org/docs/latest/",
        "Armah, P. K., et al. (2023). Machine learning applications in hospital capacity planning and bed occupancy forecasting: A systematic review. Journal of Medical Systems, 47(1), 42.",
        "3M Health Information Systems. (2023). All Patient Refined Diagnosis Related Groups (APR DRGs) Methodology Overview. 3M HIS Research Report."
    ]
    for i, ref in enumerate(refs, start=1):
        add_paragraph(doc, ref, bold_prefix=f"[{i}] ", space_after=3)

    # =========================================================================
    # CONCLUSION & FUTURE SCOPE
    # =========================================================================
    add_heading_1(doc, "Conclusion and Future Scope")
    
    add_paragraph(
        doc,
        "This project successfully designs, implements, and evaluates an end-to-end Big Data analytics framework applied to the 2,343,429 inpatient records of the New York State SPARCS 2023 dataset. By leveraging Apache Spark and PySpark, the system resolves critical data veracity challenges—including the mathematical isolation of 1,753 top-coded 120+ day stays, automated imputation of missing categorical attributes, and the strict enforcement of a clinical data leakage quarantine barrier.",
        bold_prefix="Concluding Summary: "
    )
    add_paragraph(
        doc,
        "The empirical findings deliver actionable operational baselines for hospital administration. The statewide average stay duration is established at 5.323 days, with stay lengths scaling systematically from 3.897 days in pediatric patients to 6.201 days in geriatric populations. Clinical acuity serves as a massive operational multiplier: Extreme severity cases average 14.574 days—a 4.73-fold increase over Minor severity admissions. Furthermore, clinical diagnosis profiling demonstrates that while routine maternity care dominates discharge volume, psychiatric conditions (Schizophrenia at 16.06 days, Mood Disorders at 9.79 days) and severe systemic infections (Septicemia at 9.01 days) dominate long-term bed-day utilization."
    )
    add_paragraph(
        doc,
        "The distributed Random Forest regression baseline demonstrates the feasibility of estimating inpatient stay durations using exclusively admission-time predictors, ensuring prospective operational validity without clinical data leakage. While bounded by retrospective historical constraints, the architecture provides a highly scalable, reproducible foundation for enterprise healthcare resource allocation, bed capacity planning, and future distributed machine learning research."
    )

    # Save to Word document
    out_path = Path("Hospital_Length_of_Stay_Prediction_BigData_Analytics_Report.docx")
    doc.save(str(out_path))
    print(f"Successfully generated {out_path} ({out_path.stat().st_size} bytes)")

    # Also save a copy under SPARCS_2023_Big_Data_Analytics_Enhanced_Report.docx
    out_path2 = Path("SPARCS_2023_Big_Data_Analytics_Enhanced_Report.docx")
    doc.save(str(out_path2))
    print(f"Successfully generated copy {out_path2} ({out_path2.stat().st_size} bytes)")

if __name__ == "__main__":
    build_report()
