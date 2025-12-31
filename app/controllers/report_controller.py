from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.responses import StreamingResponse
import io
import pandas as pd
import datetime
from typing import Literal

# PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics

from app.config.db import get_db
from app.services import report_service

router = APIRouter()

COMPANY_NAME = "PRINCE TUFU SUPPORT SYSTEM"
REPORT_TITLE = "REPORT DATA"


# ===================== HELPER =====================
def format_date(value):
    if value is None or pd.isna(value):
        return ""
    try:
        return pd.to_datetime(value).strftime("%d-%b-%Y")  # dd-MMM-yyyy
    except Exception:
        return str(value)


def calc_col_widths(
    df: pd.DataFrame, max_width: float, font="Helvetica", font_size=9, padding=12
):
    col_widths = []
    min_col_width = 50  # minimum width in points, prevents breaking headers
    for col in df.columns:
        # measure header
        max_col_width = pdfmetrics.stringWidth(str(col), font, font_size)
        # measure data
        for val in df[col].astype(str):
            w = pdfmetrics.stringWidth(val, font, font_size)
            if w > max_col_width:
                max_col_width = w
        col_widths.append(max(max_col_width + padding, min_col_width))

    total_width = sum(col_widths)
    if total_width > max_width:
        scale = max_width / total_width
        col_widths = [w * scale for w in col_widths]

    return col_widths


# ===================== ROUTES =====================
@router.get("/reports-testing")
def get_reports_testing(db: Session = Depends(get_db)):
    return db.execute(text("SELECT * FROM v_ticket_reports")).mappings().all()


@router.get("/reports")
def get_reports(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return report_service.getReports(db, from_date, to_date, status)


@router.get("/reports/export")
def export_reports(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    status: str | None = Query(None),
    export_type: Literal["csv", "excel", "pdf"] = Query("csv", alias="type"),
    db: Session = Depends(get_db),
):
    reports = report_service.getReports(db, from_date, to_date, status)

    if not reports:
        raise HTTPException(status_code=404, detail="No report data found")

    df = pd.DataFrame(reports)

    # rename columns to standard
    df = df.rename(
        columns={
            "ID": "id",
            "Title": "title",
            "Department": "department",
            "Category": "category",
            "Priority": "priority",
            "Status": "status",
            "Assigned To": "assigned_to",
            "Created At": "create_date",
        }
    )

    # enforce column order
    df = df[
        [
            "id",
            "title",
            "department",
            "category",
            "priority",
            "status",
            "assigned_to",
            "create_date",
        ]
    ]

    if export_type == "csv":
        return _export_csv(df)
    if export_type == "excel":
        return _export_excel(df, from_date, to_date)
    if export_type == "pdf":
        return _export_pdf(df, from_date, to_date)


# ===================== CSV =====================
def _export_csv(df: pd.DataFrame) -> StreamingResponse:
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].apply(format_date)

    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=report.csv"
    return response


# ===================== EXCEL =====================
def _export_excel(df: pd.DataFrame, from_date: str | None, to_date: str | None):
    stream = io.BytesIO()

    with pd.ExcelWriter(stream, engine="xlsxwriter") as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet("Reports")  # type: ignore
        writer.sheets["Reports"] = worksheet

        header = workbook.add_format( # type: ignore
            {
                "bold": True,
                "font_size": 14,
                "align": "center",
                "valign": "vcenter",
                "bg_color": "#2c3e50",
                "font_color": "white",
            }
        )
        sub_header = workbook.add_format( # type: ignore
            {"align": "center", "font_size": 11, "bg_color": "#ecf0f1"}
        )
        col_header = workbook.add_format( # type: ignore
            {
                "bold": True,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "bg_color": "#34495e",
                "font_color": "white",
            }
        )
        cell = workbook.add_format({"border": 1, "valign": "vcenter"}) # type: ignore
        cell_right = workbook.add_format( # type: ignore
            {"border": 1, "align": "right", "valign": "vcenter"}
        )
        date_cell = workbook.add_format( # type: ignore
            {"border": 1, "num_format": "dd-mmm-yyyy", "valign": "vcenter"}
        )

        last_col = len(df.columns) - 1
        worksheet.merge_range(0, 0, 0, last_col, f"{COMPANY_NAME} - REPORT", header)
        period = f"From: {from_date or 'All time'} | To: {to_date or 'Present'}"
        worksheet.merge_range(1, 0, 1, last_col, period, sub_header)

        for col, name in enumerate(df.columns):
            worksheet.write(3, col, name, col_header)

        for row_idx, row in enumerate(df.itertuples(index=False), start=4):
            for col_idx, value in enumerate(row):
                if isinstance(value, (pd.Timestamp, datetime.date, datetime.datetime)):
                    worksheet.write_datetime(row_idx, col_idx, value, date_cell)
                elif isinstance(value, (int, float)):
                    worksheet.write(row_idx, col_idx, value, cell_right)
                else:
                    worksheet.write(row_idx, col_idx, value, cell)

        for col_idx, col_name in enumerate(df.columns):
            max_length = max(
                len(str(col_name)), *(len(str(val)) for val in df[col_name].astype(str))
            )
            worksheet.set_column(col_idx, col_idx, min(max_length + 2, 40))

        worksheet.freeze_panes(4, 0)

    stream.seek(0)
    response = StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response.headers["Content-Disposition"] = "attachment; filename=report.xlsx"
    return response


# ===================== PDF =====================
def _export_pdf(df: pd.DataFrame, from_date: str | None, to_date: str | None):
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].apply(format_date)

    stream = io.BytesIO()
    doc = SimpleDocTemplate(
        stream,
        pagesize=landscape(A4),
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=1,
        fontSize=18,
        textColor=colors.white,
        fontName="Helvetica-Bold",
    )
    meta_style = ParagraphStyle(
        "Meta", parent=styles["Normal"], alignment=1, fontSize=9, textColor=colors.grey
    )
    cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=9, leading=11)
    header_style = ParagraphStyle(
        "Header",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.white,
        alignment=1,
        fontName="Helvetica-Bold",
    )

    # Header
    header = Table(
        [[Paragraph(COMPANY_NAME, title_style)]], colWidths=[doc.width], rowHeights=40
    )
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    elements.append(header)
    elements.append(Spacer(1, 10))

    # Title & Meta
    elements.append(Paragraph(REPORT_TITLE, styles["Heading2"]))
    period = f"Period: {from_date or 'All time'} → {to_date or 'Present'}"
    generated = f"Generated: {datetime.datetime.now():%d-%b-%Y %H:%M:%S}"
    elements.append(Paragraph(period, meta_style))
    elements.append(Paragraph(generated, meta_style))
    elements.append(Spacer(1, 15))

    # Table data
    table_data = [[Paragraph(str(col), header_style) for col in df.columns]]
    for _, row in df.iterrows():
        table_data.append([Paragraph(str(val), cell_style) for val in row])

    # Column widths responsive to header & body
    col_widths = calc_col_widths(df, doc.width)

    # Create table
    table = Table(table_data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")

    # Table style
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.whitesmoke, colors.HexColor("#f4f6f7")],
            ),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
        ]
    )
    for i, col in enumerate(df.columns):
        if pd.api.types.is_numeric_dtype(df[col]):
            style.add("ALIGN", (i, 1), (i, -1), "RIGHT")
    table.setStyle(style)
    elements.append(table)

    # Footer
    def footer(canvas, doc):
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(
            doc.pagesize[0] - doc.rightMargin,
            0.4 * inch,
            f"Page {canvas.getPageNumber()}",
        )

    doc.build(elements, onFirstPage=footer, onLaterPages=footer)

    stream.seek(0)
    response = StreamingResponse(stream, media_type="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=report.pdf"
    return response
