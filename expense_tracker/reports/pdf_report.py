"""
pdf_report.py
Generates a polished PDF financial report using ReportLab, including
a title, date range, totals, category summary, and full transaction table.
"""

from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

from services.analytics_service import (
    get_summary, get_category_wise_expenses, get_transactions_dataframe
)

DARK_HEADER = colors.HexColor("#1F2937")
INCOME_GREEN = colors.HexColor("#15803D")
EXPENSE_RED = colors.HexColor("#B91C1C")
LIGHT_GREY = colors.HexColor("#F3F4F6")


def export_pdf_report(user_id: int, filepath: str, report_title: str = "Financial Summary Report",
                       start_date: str = None, end_date: str = None, currency: str = "Rs.") -> None:
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                             topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                             leftMargin=1.5 * cm, rightMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"],
                                  textColor=DARK_HEADER, fontSize=20)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
                                     textColor=colors.grey, fontSize=10)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"],
                                    textColor=DARK_HEADER, spaceBefore=14, spaceAfter=8)

    elements = []
    elements.append(Paragraph("ExpensePro", title_style))
    elements.append(Paragraph(report_title, styles["Heading2"]))
    period_text = f"Period: {start_date or 'All time'} &nbsp;&mdash;&nbsp; {end_date or 'Present'}"
    elements.append(Paragraph(period_text, subtitle_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                               subtitle_style))
    elements.append(Spacer(1, 0.6 * cm))

    # ---- Summary Table ----
    summary = get_summary(user_id, start_date, end_date)
    summary_data = [
        ["Metric", "Value"],
        ["Total Income", f"{currency} {summary['total_income']:,.2f}"],
        ["Total Expenses", f"{currency} {summary['total_expenses']:,.2f}"],
        ["Total Savings", f"{currency} {summary['total_savings']:,.2f}"],
        ["Savings Rate", f"{summary['savings_rate']:.1f}%"],
    ]
    summary_table = Table(summary_data, colWidths=[8 * cm, 8 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TEXTCOLOR", (1, 1), (1, 1), INCOME_GREEN),
        ("TEXTCOLOR", (1, 2), (1, 2), EXPENSE_RED),
    ]))
    elements.append(Paragraph("Overview", section_style))
    elements.append(summary_table)

    # ---- Category Summary ----
    elements.append(Paragraph("Category-wise Expense Summary", section_style))
    categories = get_category_wise_expenses(user_id, start_date, end_date)
    if categories:
        cat_data = [["Category", "Amount"]] + [
            [cat, f"{currency} {amt:,.2f}"] for cat, amt in categories.items()
        ]
        cat_table = Table(cat_data, colWidths=[8 * cm, 8 * cm])
        cat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK_HEADER),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(cat_table)
    else:
        elements.append(Paragraph("No expense data available for this period.", styles["Normal"]))

    elements.append(PageBreak())

    # ---- Transaction Table ----
    elements.append(Paragraph("Transaction Details", section_style))
    df = get_transactions_dataframe(user_id, start_date, end_date)
    if not df.empty:
        table_data = [["Date", "Title", "Category", "Type", "Method", "Amount"]]
        for _, row in df.iterrows():
            table_data.append([
                row["date"], row["title"][:20], row["category"], row["type"],
                row["payment_method"], f"{currency} {row['amount']:,.2f}",
            ])
        tx_table = Table(table_data, repeatRows=1,
                          colWidths=[2.2 * cm, 4 * cm, 2.8 * cm, 2 * cm, 2.7 * cm, 3 * cm])
        style_cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), DARK_HEADER),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
        for i, (_, row) in enumerate(df.iterrows(), start=1):
            color = INCOME_GREEN if row["type"] == "Income" else EXPENSE_RED
            style_cmds.append(("TEXTCOLOR", (3, i), (3, i), color))
        tx_table.setStyle(TableStyle(style_cmds))
        elements.append(tx_table)
    else:
        elements.append(Paragraph("No transactions found for this period.", styles["Normal"]))

    doc.build(elements)
