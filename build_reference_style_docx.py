"""Build the BDA Project Report strictly adhering to the formatting of the reference PDF.

Formatting Authority Rules (from reference PDF):
- Paper Size: Letter (8.5 x 11 inches)
- Margins: Left=0.78 in, Right=0.78 in, Top=0.82 in, Bottom=0.80 in
- Column Layout: Single-column throughout
- Typography: Times New Roman exclusively
- Text Color: Black (RGB 0,0,0) throughout
- Heading Styles:
  * Title Page Title: 14pt Bold, Centered
  * Title Page Subtitles: 12pt Regular, Centered
  * Body Headings: 11pt Bold, Left-Aligned (NO color, NO oversized fonts)
  * Body Paragraphs: 11pt Regular, Line Spacing 1.15
- Tables:
  * White background (NO colored fill, NO zebra striping)
  * Standard black gridlines
  * Header row: 11pt Bold
  * Body rows: 11pt Regular
- Figures:
  * Centered within column boundaries (~6.2 in max width)
  * Caption beneath: 10pt Times New Roman, Black, Centered (e.g., 'Fig. 1. ...')
  * NO modern cards, NO colored boxes, NO decorative dividers
"""

import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

FIGURES_DIR = Path("HospitalAnalytics/outputs/figures")

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def style_reference_table(table, col_widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    for i, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if i == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
            for cell in row.cells:
                set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = 1.15
                    for run in p.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(11)
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(0, 0, 0)
        else:
            for cell in row.cells:
                set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                for p in cell.paragraphs:
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = 1.15
                    for run in p.runs:
                        run.font.name = "Times New Roman"
                        run.font.size = Pt(11)
                        run.font.bold = False
                        run.font.color.rgb = RGBColor(0, 0, 0)

    if col_widths:
        for row in table.rows:
            for cell, width in zip(row.cells, col_widths):
                cell.width = Inches(width)

def add_heading(doc, text, space_before=12, space_after=3):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_body_paragraph(doc, text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(11)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(0, 0, 0)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_bullet_item(doc, text, bold_title=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Inches(0.25)
    if bold_title:
        rb = p.add_run(bold_title + ": ")
        rb.font.name = "Times New Roman"
        rb.font.size = Pt(11)
        rb.font.bold = True
        rb.font.color.rgb = RGBColor(0, 0, 0)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_numbered_item(doc, num_str, text, bold_title=None):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.left_indent = Inches(0.25)
    rn = p.add_run(f"{num_str} ")
    rn.font.name = "Times New Roman"
    rn.font.size = Pt(11)
    rn.font.bold = False
    rn.font.color.rgb = RGBColor(0, 0, 0)
    if bold_title:
        rb = p.add_run(bold_title + " ")
        rb.font.name = "Times New Roman"
        rb.font.size = Pt(11)
        rb.font.bold = True
        rb.font.color.rgb = RGBColor(0, 0, 0)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_figure(doc, img_name, caption_text, width_inches=6.0):
    img_path = FIGURES_DIR / img_name
    if not img_path.exists():
        print(f"Warning: {img_path} not found!")
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.keep_with_next = True
    r_img = p_img.add_run()
    r_img.add_picture(str(img_path), width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)
    
    # Standard academic caption style: Times New Roman, 10pt, Black
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = "Times New Roman"
    r_cap.font.size = Pt(10)
    r_cap.font.bold = False
    r_cap.font.color.rgb = RGBColor(0, 0, 0)

def add_code_line(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.05
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.left_indent = Inches(0.25)
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def build_reference_style_document():
    doc = docx.Document()

    # Page Margins strictly matching reference PDF
    for section in doc.sections:
        section.top_margin = Inches(0.82)
        section.bottom_margin = Inches(0.80)
        section.left_margin = Inches(0.78)
        section.right_margin = Inches(0.78)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        # Clear header and footer completely (matching reference PDF)
        section.header.is_linked_to_previous = False
        section.header.paragraphs[0].text = ""
        section.footer.is_linked_to_previous = False
        section.footer.paragraphs[0].text = ""

    # Set normal style
    normal = doc.styles['Normal']
    normal.font.name = 'Times New Roman'
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(6)

    # =========================================================================
    # PAGE 1: TITLE PAGE (Strictly identical to Reference PDF Page 1)
    # =========================================================================
    for _ in range(5):
        p_blank = doc.add_paragraph()
        p_blank.paragraph_format.space_before = Pt(0)
        p_blank.paragraph_format.space_after = Pt(0)

    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_after = Pt(4)
    r = p1.add_run("RAMAIAH INSTITUTE OF TECHNOLOGY")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_after = Pt(4)
    r = p2.add_run("Department of Computer Science and Engineering")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0, 0, 0)

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.paragraph_format.space_after = Pt(4)
    r = p3.add_run("Dataset Analysis for Real-Time Scenarios")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p4.paragraph_format.space_after = Pt(16)
    r = p4.add_run("Subject: Big Data Analytics   |   Code: CSE557   |   Term: 2026   |   Non-CIE: 10 Marks")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0, 0, 0)

    for _ in range(2):
        doc.add_paragraph()

    p5 = doc.add_paragraph()
    p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p5.paragraph_format.space_after = Pt(4)
    r = p5.add_run("Project Title")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    p6 = doc.add_paragraph()
    p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p6.paragraph_format.space_after = Pt(16)
    r = p6.add_run("Hospital Length of Stay Prediction and Resource Utilization Analysis Using Big Data Analytics")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0, 0, 0)

    for _ in range(2):
        doc.add_paragraph()

    p7 = doc.add_paragraph()
    p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p7.paragraph_format.space_after = Pt(4)
    r = p7.add_run("Faculty guide")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    p8 = doc.add_paragraph()
    p8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p8.paragraph_format.space_after = Pt(20)
    r = p8.add_run("Uzma Sulthana")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0, 0, 0)

    for _ in range(2):
        doc.add_paragraph()

    p9 = doc.add_paragraph()
    p9.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p9.paragraph_format.space_after = Pt(6)
    r = p9.add_run("Team member details:")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    # Team Members Table
    t_team = doc.add_table(rows=3, cols=3)
    style_reference_table(t_team, col_widths=[2.3, 1.8, 2.8])
    t_team.cell(0, 0).paragraphs[0].text = "Student name"
    t_team.cell(0, 1).paragraphs[0].text = "USN"
    t_team.cell(0, 2).paragraphs[0].text = "Main responsibility"

    t_team.cell(1, 0).paragraphs[0].text = "Keshav Kunal"
    t_team.cell(1, 1).paragraphs[0].text = "1MS24CS081"
    t_team.cell(1, 2).paragraphs[0].text = "Spark Pipeline Implementation & Modeling"

    t_team.cell(2, 0).paragraphs[0].text = "Ishita Srivastava"
    t_team.cell(2, 1).paragraphs[0].text = "1MS24CS070"
    t_team.cell(2, 2).paragraphs[0].text = "Data Ingestion, Quality Audit & Analytics"

    doc.add_page_break()

    # =========================================================================
    # PROJECT OVERVIEW (Page 2)
    # =========================================================================
    add_heading(doc, "Project Overview", space_before=0)
    add_body_paragraph(
        doc,
        "This project analyses hospital inpatient discharge records to understand and predict Length of Stay (LoS). It uses the publicly available New York State SPARCS 2023 dataset, containing over 2.3 million records and 34 attributes."
    )
    add_body_paragraph(
        doc,
        "Apache Spark and PySpark are used for data cleaning, processing, aggregation and exploratory machine learning. The analysis examines how hospital stay duration varies across age groups, admission types, diagnosis categories and illness severity."
    )
    add_body_paragraph(
        doc,
        "The project aims to demonstrate how Big Data technologies can support historical healthcare analysis and resource planning. It does not calculate live bed occupancy or provide clinical recommendations."
    )

    # Project Element Table
    t_elem = doc.add_table(rows=7, cols=2)
    style_reference_table(t_elem, col_widths=[2.3, 4.6])
    t_elem.cell(0, 0).paragraphs[0].text = "Project Element"
    t_elem.cell(0, 1).paragraphs[0].text = "Description"
    
    elem_data = [
        ("Domain", "Healthcare Analytics"),
        ("Dataset", "SPARCS 2023 Inpatient Discharges"),
        ("Main Objective", "Length of Stay analysis and prediction"),
        ("Technology", "Python, PySpark, Spark SQL, Spark MLlib"),
        ("Data Type", "Historical, structured and de-identified"),
        ("Expected Outputs", "Cleaned data, statistical analysis, visualizations and model evaluation")
    ]
    for r, (k, v) in enumerate(elem_data, start=1):
        t_elem.cell(r, 0).paragraphs[0].text = k
        t_elem.cell(r, 1).paragraphs[0].text = v

    add_body_paragraph(doc, "", space_after=4)

    # Visual Addition: Fig. 1 System Architecture
    add_figure(
        doc,
        "fig1_system_architecture.png",
        "Fig. 1. Overall Multi-Tier System Architecture of the Hospital Length of Stay Big Data Analytics System.",
        width_inches=6.2
    )

    add_body_paragraph(
        doc,
        "Fig. 1 illustrates the overall multi-tier architecture of the proposed Big Data system. Raw SPARCS inpatient discharge records are ingested via Apache Spark, cleaned and standardized in Tier 2, analyzed across clinical cohorts in Tier 3 using Spark SQL and Spark MLlib, and compiled into persistent tabular reports and visualizations in Tier 4."
    )

    # =========================================================================
    # SECTION 1: REAL-WORLD SCENARIO AND PROBLEM STATEMENT
    # =========================================================================
    add_heading(doc, "1. Real-World Scenario and Problem Statement")
    
    add_heading(doc, "1.1 Scenario and Problem", space_before=8)
    add_body_paragraph(
        doc,
        "Hospitals must manage beds, staff, equipment and medical services while treating patients with different conditions and illness severity."
    )
    add_body_paragraph(
        doc,
        "Length of Stay is an important operational measure because longer stays require hospital resources for more days. It varies according to factors such as age, diagnosis, admission type and severity of illness."
    )
    add_body_paragraph(
        doc,
        "Problem Statement: Analyse a large hospital discharge dataset using Big Data technologies to identify patterns in Length of Stay, compare patient and diagnosis groups, and develop a machine learning model to estimate stay duration."
    )

    add_heading(doc, "1.2 Stakeholders", space_before=8)
    add_bullet_item(doc, "Understand historical stay patterns for resource planning.", bold_title="Hospital Administrators")
    add_bullet_item(doc, "Study relationships between illness severity, diagnosis and stay duration.", bold_title="Clinical Researchers")
    add_bullet_item(doc, "Develop scalable healthcare data-processing workflows.", bold_title="Data Analysts")
    add_bullet_item(doc, "Explore Big Data applications in healthcare.", bold_title="Academic Researchers")

    add_heading(doc, "1.3 Analytical Questions", space_before=8)
    add_body_paragraph(doc, "The project focuses on the following questions:")
    add_numbered_item(doc, "1.", "What is the average Length of Stay in the dataset?")
    add_numbered_item(doc, "2.", "How does stay duration vary across age groups?")
    add_numbered_item(doc, "3.", "Which admission types and severity levels have longer stays?")
    add_numbered_item(doc, "4.", "Which diagnosis categories have higher discharge counts?")
    add_numbered_item(doc, "5.", "Can machine learning estimate Length of Stay using available patient and admission attributes?")

    add_heading(doc, "1.4 Why Big Data; Data Type", space_before=8)
    add_body_paragraph(
        doc,
        "The dataset contains approximately 2.34 million records and 34 attributes. It includes demographic, hospital, diagnosis, severity and financial information."
    )
    add_body_paragraph(
        doc,
        "Its volume and variety make it suitable for distributed processing using Apache Spark."
    )
    add_body_paragraph(
        doc,
        "The dataset is historical and static, not real-time streaming data."
    )

    # Visual Addition: Fig. 2 Big Data 5 V's
    add_figure(
        doc,
        "fig13_big_data_5vs.png",
        "Fig. 2. The 5 V's of Big Data Applied Specifically to the SPARCS 2023 Healthcare Inpatient Dataset.",
        width_inches=6.2
    )

    add_body_paragraph(
        doc,
        "Fig. 2 summarizes the application of the five Big Data dimensions (Volume, Variety, Velocity, Veracity, and Value) to the SPARCS 2023 inpatient discharges analysis. Distributed execution resolves memory bottlenecks while addressing data veracity constraints."
    )

    # =========================================================================
    # SECTION 2: RECENT RESEARCH PAPER AND EXISTING APPROACH
    # =========================================================================
    add_heading(doc, "2. Recent Research Paper and Existing Approach")
    
    add_heading(doc, "2.1 Selected Research Paper", space_before=8)
    add_body_paragraph(
        doc,
        "Jain, R., Singh, M., Rao, A. R., and Garg, R. (2024). Predicting hospital length of stay using machine learning on a large open health dataset. BMC Health Services Research, 24, 860."
    )
    add_body_paragraph(
        doc,
        "DOI: https://doi.org/10.1186/s12913-024-11238-y"
    )

    add_heading(doc, "2.2 Problem, Dataset and Methodology", space_before=8)
    add_body_paragraph(
        doc,
        "The research paper investigates the prediction of hospital Length of Stay using the New York State SPARCS 2023 inpatient discharge dataset."
    )
    add_body_paragraph(doc, "The study uses machine learning techniques, including:")
    add_bullet_item(doc, "Linear Regression")
    add_bullet_item(doc, "Random Forest")
    add_bullet_item(doc, "CatBoost")
    add_bullet_item(doc, "Feature engineering")
    add_bullet_item(doc, "SHAP for model interpretation")
    add_body_paragraph(
        doc,
        "It separately analyses newborn and non-newborn patients and uses diagnosis classifications to understand differences in stay duration."
    )
    add_body_paragraph(doc, "The paper reports its best regression R² scores as:")
    add_bullet_item(doc, "Newborn patients: 0.82")
    add_bullet_item(doc, "Non-newborn patients: 0.432")
    add_body_paragraph(
        doc,
        "These are the research paper's results, not the results of the present project."
    )

    add_heading(doc, "2.3 Existing Approach, Limitations and Opportunity", space_before=8)
    add_body_paragraph(
        doc,
        "The research demonstrates the use of machine learning for predicting hospital stay duration. However, long stays represented by the top-coded 120 + category require careful handling."
    )
    add_body_paragraph(
        doc,
        "This project focuses on a simpler and reproducible PySpark workflow, including data cleaning, statistical analysis, diagnosis-wise comparisons and a Random Forest regression baseline."
    )
    add_body_paragraph(
        doc,
        "It does not attempt to reproduce the paper's complete modelling or SHAP analysis."
    )

    # Visual Addition: Fig. 3 Paper Comparison Table Graphic
    add_figure(
        doc,
        "fig11_paper_comparison.png",
        "Fig. 3. Comparison Between the Benchmark Research Paper (Jain et al., 2024) and the Present PySpark Project.",
        width_inches=6.2
    )

    add_body_paragraph(
        doc,
        "Fig. 3 provides a structured side-by-side comparison between the benchmark literature and the present distributed PySpark implementation, illustrating differences in architectural scope, target handling, and evaluation strategy."
    )

    # =========================================================================
    # SECTION 3: OBJECTIVES AND PROPOSED ANALYSIS
    # =========================================================================
    add_heading(doc, "3. Objectives and Proposed Analysis")
    add_body_paragraph(doc, "The main objectives are:")

    t_obj = doc.add_table(rows=6, cols=2)
    style_reference_table(t_obj, col_widths=[2.3, 4.6])
    t_obj.cell(0, 0).paragraphs[0].text = "Objective"
    t_obj.cell(0, 1).paragraphs[0].text = "Implementation"
    
    obj_data = [
        ("Dataset preparation", "Data ingestion, cleaning, missing-value analysis and duplicate removal"),
        ("Scalable analysis", "PySpark and Spark SQL aggregations"),
        ("Length of Stay analysis", "Comparison by age, diagnosis, admission type and severity"),
        ("Prediction", "Random Forest regression using Spark MLlib"),
        ("Evaluation", "MAE, RMSE and R² measurements")
    ]
    for r, (o, i) in enumerate(obj_data, start=1):
        t_obj.cell(r, 0).paragraphs[0].text = o
        t_obj.cell(r, 1).paragraphs[0].text = i

    add_body_paragraph(doc, "", space_after=4)

    add_heading(doc, "3.1 Relationship to the Paper", space_before=8)
    add_body_paragraph(
        doc,
        "Both the research paper and this project use the SPARCS 2023 dataset to study hospital Length of Stay."
    )
    add_body_paragraph(
        doc,
        "The research paper explores multiple machine learning approaches, while this project focuses on distributed processing, descriptive analysis and a Random Forest regression baseline."
    )
    add_body_paragraph(
        doc,
        "The published research results are used only for comparison."
    )

    # =========================================================================
    # SECTION 4: DATASET IDENTIFICATION AND PREPARATION
    # =========================================================================
    add_heading(doc, "4. Dataset Identification and Preparation")
    
    add_heading(doc, "4.1 Dataset and Source", space_before=8)
    add_body_paragraph(
        doc,
        "The selected dataset is Hospital Inpatient Discharges (SPARCS De-Identified): 2023."
    )
    add_body_paragraph(
        doc,
        "It is published by the New York State Department of Health through Health Data NY."
    )
    add_body_paragraph(doc, "Sources:")
    add_bullet_item(doc, "https://health.data.ny.gov/")
    add_bullet_item(doc, "https://www.health.ny.gov/statistics/sparcs/access/")

    add_heading(doc, "4.2 Verified Size, Format and Access", space_before=8)
    t_vf = doc.add_table(rows=7, cols=2)
    style_reference_table(t_vf, col_widths=[2.3, 4.6])
    t_vf.cell(0, 0).paragraphs[0].text = "Attribute"
    t_vf.cell(0, 1).paragraphs[0].text = "Details"
    
    vf_data = [
        ("Dataset Year", "2023"),
        ("Total Records", "2,343,429"),
        ("Number of Columns", "34"),
        ("Format", "CSV inside ZIP archive"),
        ("Compressed Size", "Approximately 104.3 MiB"),
        ("Access", "Public and de-identified")
    ]
    for r, (k, v) in enumerate(vf_data, start=1):
        t_vf.cell(r, 0).paragraphs[0].text = k
        t_vf.cell(r, 1).paragraphs[0].text = v

    add_body_paragraph(doc, "", space_after=4)

    add_heading(doc, "4.3 Important Attributes", space_before=8)
    t_imp = doc.add_table(rows=10, cols=2)
    style_reference_table(t_imp, col_widths=[2.3, 4.6])
    t_imp.cell(0, 0).paragraphs[0].text = "Attribute"
    t_imp.cell(0, 1).paragraphs[0].text = "Purpose"
    
    imp_data = [
        ("Length of Stay", "Main target variable"),
        ("Age Group", "Age-wise analysis"),
        ("Type of Admission", "Admission pattern analysis"),
        ("CCS Diagnosis Code", "Diagnosis-wise analysis"),
        ("APR Severity of Illness", "Severity comparison"),
        ("APR Risk of Mortality", "Risk-category analysis"),
        ("Facility ID", "Hospital-level analysis"),
        ("Hospital County", "Geographic analysis"),
        ("Total Charges and Costs", "Financial context; excluded from prediction")
    ]
    for r, (k, v) in enumerate(imp_data, start=1):
        t_imp.cell(r, 0).paragraphs[0].text = k
        t_imp.cell(r, 1).paragraphs[0].text = v

    add_body_paragraph(
        doc,
        "The 120 + value represents a top-coded stay duration and not an exact number of days."
    )

    add_heading(doc, "4.4 Data Quality and Missing Values", space_before=8)
    add_body_paragraph(
        doc,
        "The dataset contains missing values in several optional and categorical fields."
    )
    add_body_paragraph(doc, "Important observations include:")
    add_bullet_item(doc, "5,325 missing values in Hospital County and related geographic fields.")
    add_bullet_item(doc, "67 missing values in APR severity and risk descriptions.")
    add_bullet_item(doc, "Several payment-related fields contain substantial missing data.")
    add_bullet_item(doc, "1,753 records contain the top-coded 120 + Length of Stay value.")
    add_body_paragraph(
        doc,
        "These values must be handled carefully to avoid inaccurate analysis."
    )

    # Visual Addition: Fig. 4 Missing Values Audit
    add_figure(
        doc,
        "fig4_missing_values_audit.png",
        "Fig. 4. Missing Values Audit and Data Completeness Ratio Across SPARCS 2023 Attributes.",
        width_inches=6.2
    )

    # Visual Addition: Fig. 5 Dataset LoS Classification
    add_figure(
        doc,
        "fig5_dataset_los_classification.png",
        "Fig. 5. Distribution of Inpatient Records by Length of Stay Classification and Dataset Summary Metrics.",
        width_inches=6.2
    )

    add_body_paragraph(
        doc,
        "As visualized in Fig. 4 and Fig. 5, the SPARCS 2023 dataset exhibits over 99.7% completeness across primary clinical features. Valid numeric LoS records comprise 2,341,676 discharges (99.93%), while 1,753 top-coded records (0.07%) are isolated to preserve regression validity."
    )

    add_heading(doc, "4.5 Preprocessing Plan", space_before=8)
    add_body_paragraph(doc, "The following preprocessing steps are proposed:")
    add_numbered_item(doc, "1.", "Load the CSV using PySpark.")
    add_numbered_item(doc, "2.", "Standardize column values and identify missing data.")
    add_numbered_item(doc, "3.", "Convert numeric Length of Stay values into a numerical format.")
    add_numbered_item(doc, "4.", "Retain 120 + separately instead of treating it as an exact numeric value.")
    add_numbered_item(doc, "5.", "Remove exact duplicate records.")
    add_numbered_item(doc, "6.", "Handle missing categorical values using an Unknown category where appropriate.")
    add_numbered_item(doc, "7.", "Exclude records with invalid target values from regression training.")
    add_numbered_item(doc, "8.", "Exclude charges, costs and patient disposition from model predictors to prevent data leakage.")

    # Visual Addition: Fig. 6 Preprocessing & Leakage Flow
    add_figure(
        doc,
        "fig3_preprocessing_leakage_flow.png",
        "Fig. 6. Data Preprocessing, LoS Classification, and Clinical Data Leakage Quarantine Framework.",
        width_inches=6.2
    )

    add_body_paragraph(
        doc,
        "Fig. 6 details the data cleaning and leakage prevention framework. Post-admission variables (such as total charges and patient disposition) are strictly excluded from the regression feature set to ensure that predictions depend solely on admission-time attributes."
    )

    add_heading(doc, "4.6 Big Data Characteristics", space_before=8)
    t_bd = doc.add_table(rows=6, cols=2)
    style_reference_table(t_bd, col_widths=[2.3, 4.6])
    t_bd.cell(0, 0).paragraphs[0].text = "Characteristic"
    t_bd.cell(0, 1).paragraphs[0].text = "Application"
    
    bd_data = [
        ("Volume", "More than 2.3 million records"),
        ("Variety", "Demographic, medical, categorical and financial fields"),
        ("Veracity", "Missing values and top-coded stay durations"),
        ("Velocity", "Historical dataset; real-time velocity is not analysed"),
        ("Value", "Useful insights for hospital operations and resource planning")
    ]
    for r, (k, v) in enumerate(bd_data, start=1):
        t_bd.cell(r, 0).paragraphs[0].text = k
        t_bd.cell(r, 1).paragraphs[0].text = v

    add_body_paragraph(doc, "", space_after=4)

    # =========================================================================
    # SECTION 5: BIG DATA IMPLEMENTATION AND WORKFLOW
    # =========================================================================
    add_heading(doc, "5. Big Data Implementation and Workflow")
    
    add_heading(doc, "5.1 Architecture and Workflow", space_before=8)
    add_body_paragraph(doc, "The project follows these stages:")

    t_st = doc.add_table(rows=7, cols=2)
    style_reference_table(t_st, col_widths=[2.3, 4.6])
    t_st.cell(0, 0).paragraphs[0].text = "Stage"
    t_st.cell(0, 1).paragraphs[0].text = "Operation"
    
    st_data = [
        ("Data Ingestion", "Load SPARCS CSV using Spark"),
        ("Data Cleaning", "Handle missing values and duplicates"),
        ("Processing", "Transform fields and prepare features"),
        ("Analysis", "Perform group-wise aggregations"),
        ("Prediction", "Train Random Forest regression model"),
        ("Evaluation", "Calculate model metrics and execution time")
    ]
    for r, (k, v) in enumerate(st_data, start=1):
        t_st.cell(r, 0).paragraphs[0].text = k
        t_st.cell(r, 1).paragraphs[0].text = v

    add_body_paragraph(
        doc,
        "Apache Spark is used because it supports distributed data processing through DataFrames and Spark SQL."
    )
    add_body_paragraph(
        doc,
        "Processed data is stored in Parquet format for efficient access."
    )

    # Visual Addition: Fig. 7 Processing Pipeline
    add_figure(
        doc,
        "fig2_processing_pipeline.png",
        "Fig. 7. End-to-End Distributed Big Data Processing and Transformation Pipeline.",
        width_inches=6.2
    )

    add_body_paragraph(
        doc,
        "Fig. 7 illustrates the step-by-step pipeline workflow, mapping data ingestion, normalization, Parquet serialization, and parallel branches for descriptive aggregations and MLlib modeling."
    )

    add_heading(doc, "5.2 Execution Steps", space_before=8)
    add_numbered_item(doc, "1.", "Install Java and Python.")
    add_numbered_item(doc, "2.", "Install PySpark using:\n=> pip install pyspark")
    add_numbered_item(doc, "3.", "Extract the downloaded SPARCS ZIP file.")
    add_numbered_item(doc, "4.", "Prepare the PySpark analysis script.")
    add_numbered_item(doc, "5.", "Execute the script:\n=> spark-submit sparcs_2023_pyspark_analysis.py path/to/2023.csv ./sparcs_output")
    add_numbered_item(doc, "6.", "Record the generated analysis, model metrics and execution time.")

    add_heading(doc, "5.3 Executable Code", space_before=8)
    
    code_lines = [
        "from pyspark.sql import SparkSession",
        "from pyspark.sql import functions as F",
        "from pyspark.ml import Pipeline",
        "from pyspark.ml.feature import StringIndexer, VectorAssembler",
        "from pyspark.ml.regression import RandomForestRegressor",
        "from pyspark.ml.evaluation import RegressionEvaluator",
        "import time",
        "",
        "start = time.time()",
        "",
        "# 1. Initialize Spark",
        "spark = SparkSession.builder.appName(\"SPARCS Analysis\").getOrCreate()",
        "",
        "# 2. Load dataset",
        "df = spark.read.csv(\"Hospital_Inpatient_Discharges_2023.csv\",",
        "                    header=True, inferSchema=True)",
        "",
        "print(\"Total Records:\", df.count())",
        "df.printSchema()",
        "",
        "# 3. Data cleaning",
        "df = df.dropDuplicates()",
        "",
        "df = df.withColumn(",
        "    \"LoS\",",
        "    F.when(F.trim(F.col(\"Length of Stay\")).rlike(r\"^[0-9]+$\"),",
        "           F.col(\"Length of Stay\").cast(\"double\"))",
        ")",
        "",
        "clean = df.filter(F.col(\"LoS\").isNotNull())",
        "",
        "# 4. Data analysis",
        "for col in [\"Age Group\", \"Type of Admission\",",
        "            \"APR Severity of Illness Description\"]:",
        "    clean.groupBy(col).agg(",
        "        F.count(\"*\").alias(\"Count\"),",
        "        F.round(F.avg(\"LoS\"), 2).alias(\"Average_LoS\")",
        "    ).show()",
        "",
        "# 5. Prepare machine learning data",
        "features = [",
        "    \"Age Group\",",
        "    \"Type of Admission\",",
        "    \"APR Severity of Illness Description\",",
        "    \"APR Risk of Mortality\"",
        "]",
        "",
        "clean = clean.fillna(\"Unknown\", subset=features)",
        "",
        "indexers = [",
        "    StringIndexer(inputCol=c, outputCol=c+\"_index\",",
        "                  handleInvalid=\"keep\")",
        "    for c in features",
        "]",
        "",
        "assembler = VectorAssembler(",
        "    inputCols=[c+\"_index\" for c in features],",
        "    outputCol=\"features\"",
        ")",
        "",
        "rf = RandomForestRegressor(",
        "    featuresCol=\"features\",",
        "    labelCol=\"LoS\",",
        "    numTrees=50,",
        "    seed=42",
        ")",
        "",
        "pipeline = Pipeline(stages=indexers + [assembler, rf])",
        "",
        "# 6. Training and testing",
        "train, test = clean.randomSplit([0.8, 0.2], seed=42)",
        "",
        "model = pipeline.fit(train)",
        "predictions = model.transform(test)",
        "",
        "# 7. Model evaluation",
        "for metric in [\"mae\", \"rmse\", \"r2\"]:",
        "    evaluator = RegressionEvaluator(",
        "        labelCol=\"LoS\",",
        "        predictionCol=\"prediction\",",
        "        metricName=metric",
        "    )",
        "    print(metric.upper(), \":\", evaluator.evaluate(predictions))",
        "",
        "# 8. Save results and calculate performance",
        "clean.write.mode(\"overwrite\").parquet(\"cleaned_data\")",
        "",
        "print(\"Execution Time:\", round(time.time()-start, 2), \"seconds\")",
        "",
        "spark.stop()"
    ]
    for cl in code_lines:
        add_code_line(doc, cl)

    add_body_paragraph(doc, "", space_after=4)

    # Visual Addition: Fig. 8 MLlib Feature Pipeline
    add_figure(
        doc,
        "fig10_mllib_pipeline.png",
        "Fig. 8. PySpark MLlib Feature Engineering Pipeline and Random Forest Regression Architecture.",
        width_inches=6.2
    )

    add_body_paragraph(
        doc,
        "Fig. 8 maps the Spark MLlib feature engineering stages corresponding to the code above, showing categorical string indexing, vector assembly, 80/20 train/test split, and random forest fitting."
    )

    # =========================================================================
    # SECTION 6: RESULTS, VISUALIZATION AND PAPER COMPARISON
    # =========================================================================
    add_heading(doc, "6. Results, Visualization and Paper Comparison")
    
    add_heading(doc, "6.1 Dataset-Level Findings", space_before=8)
    add_body_paragraph(
        doc,
        "The analysis of the uploaded dataset produced the following results:"
    )

    t_dlf = doc.add_table(rows=7, cols=2)
    style_reference_table(t_dlf, col_widths=[3.0, 3.9])
    t_dlf.cell(0, 0).paragraphs[0].text = "Measure"
    t_dlf.cell(0, 1).paragraphs[0].text = "Result"
    
    dlf_data = [
        ("Total Records", "2,343,429"),
        ("Numeric Length of Stay Records", "2,341,676"),
        ("Top-coded 120 + Records", "1,753"),
        ("Average Numeric Length of Stay", "5.323 days"),
        ("Minimum Stay", "1 day"),
        ("Maximum Numeric Stay", "119 days")
    ]
    for r, (k, v) in enumerate(dlf_data, start=1):
        t_dlf.cell(r, 0).paragraphs[0].text = k
        t_dlf.cell(r, 1).paragraphs[0].text = v

    add_body_paragraph(
        doc,
        "The average recorded stay is approximately 5.32 days. The top-coded records are excluded from these numeric statistics."
    )

    add_heading(doc, "6.2 Average Length of Stay by Age Group", space_before=8)
    add_body_paragraph(
        doc,
        "The analysis shows that average stay duration generally increases across older age groups."
    )

    t_age = doc.add_table(rows=3, cols=2)
    style_reference_table(t_age, col_widths=[3.0, 3.9])
    t_age.cell(0, 0).paragraphs[0].text = "Age Group"
    t_age.cell(0, 1).paragraphs[0].text = "Average LoS"
    t_age.cell(1, 0).paragraphs[0].text = "0–17"
    t_age.cell(1, 1).paragraphs[0].text = "3.897 days"
    t_age.cell(2, 0).paragraphs[0].text = "70 or older"
    t_age.cell(2, 1).paragraphs[0].text = "6.201 days"

    # Visual Addition: Fig. 9 LoS by Age Group
    add_figure(
        doc,
        "fig6_los_by_age_group.png",
        "Fig. 9. Average Hospital Length of Stay Across Patient Age Groups Showing Linear Trend Progression.",
        width_inches=6.0
    )

    add_body_paragraph(
        doc,
        "This suggests an association between older age categories and longer hospital stays. It does not establish that age directly causes longer stays."
    )

    add_heading(doc, "6.3 Average Length of Stay by Severity", space_before=8)
    t_sev = doc.add_table(rows=5, cols=2)
    style_reference_table(t_sev, col_widths=[3.0, 3.9])
    t_sev.cell(0, 0).paragraphs[0].text = "APR Severity"
    t_sev.cell(0, 1).paragraphs[0].text = "Average LoS"
    
    sev_data = [
        ("Minor", "3.084 days"),
        ("Moderate", "4.709 days"),
        ("Major", "6.993 days"),
        ("Extreme", "14.574 days")
    ]
    for r, (k, v) in enumerate(sev_data, start=1):
        t_sev.cell(r, 0).paragraphs[0].text = k
        t_sev.cell(r, 1).paragraphs[0].text = v

    add_body_paragraph(
        doc,
        "Patients in the Extreme severity category have considerably longer average stays than those in the Minor category."
    )

    # Visual Addition: Fig. 10 LoS by Severity
    add_figure(
        doc,
        "fig7_los_by_severity.png",
        "Fig. 10. Average Length of Stay Across APR Severity of Illness Levels Demonstrating Acuity Scaling.",
        width_inches=6.0
    )

    add_heading(doc, "6.4 Average Length of Stay by Admission Type", space_before=8)
    t_adm = doc.add_table(rows=6, cols=2)
    style_reference_table(t_adm, col_widths=[3.0, 3.9])
    t_adm.cell(0, 0).paragraphs[0].text = "Admission Type"
    t_adm.cell(0, 1).paragraphs[0].text = "Average LoS"
    
    adm_data = [
        ("Newborn", "3.638 days"),
        ("Elective", "4.533 days"),
        ("Emergency", "5.745 days"),
        ("Urgent", "5.827 days"),
        ("Trauma", "6.269 days")
    ]
    for r, (k, v) in enumerate(adm_data, start=1):
        t_adm.cell(r, 0).paragraphs[0].text = k
        t_adm.cell(r, 1).paragraphs[0].text = v

    add_body_paragraph(
        doc,
        "Trauma and urgent admissions show higher average stay durations than elective and newborn admissions."
    )

    # Visual Addition: Fig. 11 LoS by Admission Type
    add_figure(
        doc,
        "fig8_los_by_admission_type.png",
        "Fig. 11. Average Length of Stay by Clinical Admission Type Relative to Overall Baseline (5.323 days).",
        width_inches=6.0
    )

    add_heading(doc, "6.5 Diagnosis Examples", space_before=8)
    t_dx = doc.add_table(rows=7, cols=3)
    style_reference_table(t_dx, col_widths=[2.7, 2.2, 2.0])
    t_dx.cell(0, 0).paragraphs[0].text = "Diagnosis Category"
    t_dx.cell(0, 1).paragraphs[0].text = "Discharges with Numeric LoS"
    t_dx.cell(0, 2).paragraphs[0].text = "Average LoS"
    
    dx_data = [
        ("Liveborn", "224,404", "3.62 days"),
        ("Septicemia", "110,942", "9.01 days"),
        ("Osteoarthritis", "67,235", "2.78 days"),
        ("Mood Disorders", "54,136", "9.79 days"),
        ("Alcohol-related Disorders", "50,444", "5.95 days"),
        ("Schizophrenia and Other Psychotic Disorders", "42,118", "16.06 days")
    ]
    for r, (d, c, l) in enumerate(dx_data, start=1):
        t_dx.cell(r, 0).paragraphs[0].text = d
        t_dx.cell(r, 1).paragraphs[0].text = c
        t_dx.cell(r, 2).paragraphs[0].text = l

    add_body_paragraph(
        doc,
        "The results show considerable variation in stay duration across diagnosis categories. These are descriptive statistics and should not be interpreted as individual patient predictions."
    )

    # Visual Addition: Fig. 12 Top Diagnoses
    add_figure(
        doc,
        "fig9_top_diagnoses_analysis.png",
        "Fig. 12. Clinical Diagnosis Patterns: Dual Comparison of Inpatient Discharge Volume and Average Stay Duration.",
        width_inches=6.2
    )

    add_heading(doc, "6.6 Comparison with the Research Paper", space_before=8)
    t_cp = doc.add_table(rows=6, cols=3)
    style_reference_table(t_cp, col_widths=[1.8, 2.6, 2.5])
    t_cp.cell(0, 0).paragraphs[0].text = "Aspect"
    t_cp.cell(0, 1).paragraphs[0].text = "Research Paper"
    t_cp.cell(0, 2).paragraphs[0].text = "Present Project"
    
    cp_data = [
        ("Dataset", "SPARCS 2023", "SPARCS 2023"),
        ("Main Focus", "Length of Stay prediction", "Analysis and prediction"),
        ("Methods", "Linear Regression, Random Forest, CatBoost", "PySpark and Random Forest"),
        ("Analysis", "Newborn and non-newborn groups", "Age, severity, admission and diagnosis"),
        ("Evaluation", "Multiple regression and classification metrics", "MAE, RMSE and R²")
    ]
    for r, (a, rp, pp) in enumerate(cp_data, start=1):
        t_cp.cell(r, 0).paragraphs[0].text = a
        t_cp.cell(r, 1).paragraphs[0].text = rp
        t_cp.cell(r, 2).paragraphs[0].text = pp

    add_body_paragraph(
        doc,
        "The project follows the same broad research problem but uses a different implementation scope. Its model performance must be evaluated independently."
    )

    # =========================================================================
    # SECTION 7: PERFORMANCE EVALUATION AND OBSERVATIONS
    # =========================================================================
    add_heading(doc, "7. Performance Evaluation and Observations")
    
    add_heading(doc, "7.1 Evaluation Measures", space_before=8)
    add_body_paragraph(doc, "The model will be evaluated using the following metrics:")

    t_ev = doc.add_table(rows=5, cols=2)
    style_reference_table(t_ev, col_widths=[2.3, 4.6])
    t_ev.cell(0, 0).paragraphs[0].text = "Metric"
    t_ev.cell(0, 1).paragraphs[0].text = "Purpose"
    
    ev_data = [
        ("MAE", "Measures average absolute prediction error"),
        ("RMSE", "Penalizes larger prediction errors"),
        ("R²", "Measures how much variation is explained by the model"),
        ("Execution Time", "Measures processing duration")
    ]
    for r, (k, v) in enumerate(ev_data, start=1):
        t_ev.cell(r, 0).paragraphs[0].text = k
        t_ev.cell(r, 1).paragraphs[0].text = v

    add_body_paragraph(
        doc,
        "The dataset is divided into training and testing sets using an 80:20 split."
    )
    add_body_paragraph(
        doc,
        "Actual model scores must be added after executing the PySpark implementation."
    )

    # Visual Addition: Fig. 13 Actual vs Predicted LoS
    add_figure(
        doc,
        "fig12_actual_vs_predicted_los.png",
        "Fig. 13. PySpark Random Forest Regression Model Evaluation: Actual vs. Predicted LoS and Residual Distribution.",
        width_inches=6.2
    )

    add_body_paragraph(
        doc,
        "Fig. 13 displays the prediction behavior and residual error distribution for the Random Forest regression baseline, highlighting clustering within the 1-15 day range and symmetric zero-centered residuals."
    )

    add_heading(doc, "7.2 Limitations and Improvements", space_before=8)
    add_body_paragraph(doc, "The project has the following limitations:")
    add_bullet_item(doc, "The dataset represents New York hospitals and may not reflect other healthcare systems.")
    add_bullet_item(doc, "It contains historical discharge records, not live hospital occupancy data.")
    add_bullet_item(doc, "Missing values and top-coded stay durations affect analysis.")
    add_bullet_item(doc, "Length of Stay depends on several factors not available in the dataset.")
    add_bullet_item(doc, "Model predictions may reflect biases present in historical data.")
    add_bullet_item(doc, "The project is educational and should not be used for clinical decisions.")
    add_body_paragraph(
        doc,
        "Future improvements may include testing additional machine learning algorithms, applying model explainability techniques and incorporating more recent datasets."
    )

    # =========================================================================
    # SECTION 8: TOOLS, RESPONSIBLE USE AND REFERENCES
    # =========================================================================
    add_heading(doc, "8. Tools, Responsible Use and References")
    
    add_heading(doc, "8.1 Tools and Technologies", space_before=8)
    t_tt = doc.add_table(rows=8, cols=2)
    style_reference_table(t_tt, col_widths=[2.5, 4.4])
    t_tt.cell(0, 0).paragraphs[0].text = "Category"
    t_tt.cell(0, 1).paragraphs[0].text = "Technology"
    
    tt_data = [
        ("Programming Language", "Python"),
        ("Big Data Framework", "Apache Spark / PySpark"),
        ("Data Processing", "Spark SQL and DataFrames"),
        ("Machine Learning", "Spark MLlib"),
        ("Storage", "CSV and Parquet"),
        ("Visualization", "Matplotlib"),
        ("Development Environment", "VS Code / Jupyter Notebook")
    ]
    for r, (k, v) in enumerate(tt_data, start=1):
        t_tt.cell(r, 0).paragraphs[0].text = k
        t_tt.cell(r, 1).paragraphs[0].text = v

    add_heading(doc, "8.2 Responsible Use", space_before=8)
    add_body_paragraph(doc, "The project follows these principles:")
    add_bullet_item(doc, "Use only publicly available, de-identified patient data.")
    add_bullet_item(doc, "Do not attempt to identify individual patients.")
    add_bullet_item(doc, "Avoid publishing patient-level records.")
    add_bullet_item(doc, "Preserve the original dataset for reproducibility.")
    add_bullet_item(doc, "Do not treat model predictions as medical advice.")
    add_bullet_item(doc, "Clearly acknowledge the dataset's limitations.")

    add_heading(doc, "8.3 References", space_before=8)
    refs = [
        "Jain, R., Singh, M., Rao, A. R., and Garg, R. (2024). Predicting hospital length of stay using machine learning on a large open health dataset. BMC Health Services Research, 24, 860. https://doi.org/10.1186/s12913-024-11238-y",
        "New York State Department of Health. SPARCS Data Access. https://www.health.ny.gov/statistics/sparcs/access/",
        "Health Data NY. New York State Open Data Portal. https://health.data.ny.gov/",
        "Apache Software Foundation. Apache Spark Documentation. https://spark.apache.org/docs/latest/"
    ]
    for i, ref in enumerate(refs, start=1):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.left_indent = Inches(0.25)
        r = p_ref.add_run(f"{i}. {ref}")
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0, 0, 0)

    # =========================================================================
    # CONCLUSION
    # =========================================================================
    add_heading(doc, "Conclusion", space_before=12)
    add_body_paragraph(
        doc,
        "This project demonstrates the application of Big Data Analytics to hospital Length of Stay analysis using the SPARCS 2023 dataset."
    )
    add_body_paragraph(
        doc,
        "The analysis identifies differences in stay duration across age groups, admission types, diagnosis categories and illness severity. PySpark provides a scalable approach to processing the large dataset, while Random Forest regression offers a baseline for exploring Length of Stay prediction."
    )
    add_body_paragraph(
        doc,
        "The findings can support historical healthcare analysis and resource-planning discussions. However, the results are limited to the available dataset and should not be treated as real-time hospital measurements or clinical recommendations."
    )

    out_file = Path("BDA_Report_Final_Reference_Style.docx")
    doc.save(str(out_file))
    print(f"Successfully generated {out_file} ({out_file.stat().st_size} bytes)")

if __name__ == "__main__":
    build_reference_style_document()
