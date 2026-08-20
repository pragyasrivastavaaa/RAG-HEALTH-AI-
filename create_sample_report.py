"""
Run this once to generate a test PDF:
    python create_sample_report.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER


def generate():
    doc = SimpleDocTemplate("sample_blood_report.pdf", pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []

    h1 = ParagraphStyle('h1', fontSize=16, fontName='Helvetica-Bold',
                         textColor=colors.HexColor('#1a3a5c'), alignment=TA_CENTER)
    h2 = ParagraphStyle('h2', fontSize=10, fontName='Helvetica',
                         textColor=colors.grey, alignment=TA_CENTER)

    story.append(Paragraph("PATHOLOGY LABORATORY", h1))
    story.append(Paragraph("Comprehensive Blood Analysis Report", h2))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1a3a5c')))
    story.append(Spacer(1, 0.3*cm))

    info = [
        ["Patient Name:", "Rahul Sharma",      "Report No:",   "LAB-2024-001"],
        ["Age / Gender:", "35 Years / Male",   "Sample Type:", "Venous Blood"],
        ["Ref. Doctor:",  "Dr. Sample Doctor", "Date:",        "15-Jan-2024"],
    ]
    t = Table(info, colWidths=[3.5*cm, 6.5*cm, 3*cm, 5*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 0.3*cm))

    def section(title):
        s = ParagraphStyle('s', fontSize=11, fontName='Helvetica-Bold',
                           textColor=colors.white, backColor=colors.HexColor('#1a3a5c'),
                           leftIndent=6, leading=16)
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(f"  {title}", s))
        story.append(Spacer(1, 0.15*cm))

    def lab_table(rows):
        data = [["Test Name", "Result", "Unit", "Normal Range", "Status"]] + rows
        t = Table(data, colWidths=[6.5*cm, 2.5*cm, 2*cm, 4*cm, 2.5*cm])
        style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c5f8a')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0,0), (-1,-1), 9),
            ('FONTNAME',   (0,1), (-1,-1), 'Helvetica'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f5f9ff'), colors.white]),
            ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#ccddee')),
            ('ALIGN',      (1,0), (-1,-1), 'CENTER'),
            ('TOPPADDING',    (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING',   (0,0), (0,-1), 8),
        ]
        for i, row in enumerate(rows, start=1):
            if row[4] == "HIGH":
                style += [('TEXTCOLOR', (4,i), (4,i), colors.HexColor('#cc0000')),
                          ('FONTNAME',  (4,i), (4,i), 'Helvetica-Bold')]
            elif row[4] == "LOW":
                style += [('TEXTCOLOR', (4,i), (4,i), colors.HexColor('#cc6600')),
                          ('FONTNAME',  (4,i), (4,i), 'Helvetica-Bold')]
            else:
                style.append(('TEXTCOLOR', (4,i), (4,i), colors.HexColor('#007700')))
        t.setStyle(TableStyle(style))
        story.append(t)

    section("COMPLETE BLOOD COUNT")
    lab_table([
        ["Hemoglobin",    "10.5",   "g/dL",       "12.0 - 17.5",    "LOW"],
        ["RBC Count",     "3.8",    "million/uL",  "4.2 - 5.9",      "LOW"],
        ["WBC Count",     "7500",   "cells/uL",    "4000 - 11000",   "NORMAL"],
        ["Platelet Count","180000", "cells/uL",    "150000 - 400000","NORMAL"],
    ])

    section("BLOOD SUGAR")
    lab_table([
        ["Glucose Fasting", "118", "mg/dL", "70 - 100", "HIGH"],
        ["Glucose PP",      "165", "mg/dL", "70 - 140", "HIGH"],
        ["HbA1c",           "6.2", "%",     "0 - 5.7",  "HIGH"],
    ])

    section("LIPID PROFILE")
    lab_table([
        ["Total Cholesterol", "215", "mg/dL", "0 - 200",  "HIGH"],
        ["LDL Cholesterol",   "140", "mg/dL", "0 - 100",  "HIGH"],
        ["HDL Cholesterol",   "38",  "mg/dL", "40 - 999", "LOW"],
        ["Triglycerides",     "175", "mg/dL", "0 - 150",  "HIGH"],
    ])

    section("THYROID FUNCTION TEST")
    lab_table([["TSH", "5.5", "mIU/L", "0.4 - 4.0", "HIGH"]])

    section("VITAMINS")
    lab_table([
        ["Vitamin D",   "18",  "ng/mL", "30 - 100",  "LOW"],
        ["Vitamin B12", "180", "pg/mL", "200 - 900", "LOW"],
    ])

    section("LIVER FUNCTION TEST")
    lab_table([
        ["SGPT (ALT)", "52", "U/L", "0 - 40", "HIGH"],
        ["SGOT (AST)", "48", "U/L", "0 - 40", "HIGH"],
    ])

    section("KIDNEY FUNCTION TEST")
    lab_table([
        ["Creatinine", "1.4", "mg/dL", "0.6 - 1.2", "HIGH"],
        ["Uric Acid",  "7.2", "mg/dL", "2.4 - 6.0", "HIGH"],
    ])

    disc = ParagraphStyle('d', fontSize=7.5, fontName='Helvetica',
                           textColor=colors.grey, alignment=TA_CENTER)
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "This report is for testing purposes only. Always consult a qualified doctor.", disc))

    doc.build(story)
    print("sample_blood_report.pdf created successfully!")
    print("Now upload this file through the web interface.")


if __name__ == "__main__":
    generate()