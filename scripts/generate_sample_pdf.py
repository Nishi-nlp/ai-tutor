"""Generate the project-authored CC0 PDF ingestion fixture."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "tests" / "fixtures" / "pdfs" / "sample-linear-algebra.pdf"


def add_page_number(canvas, document) -> None:
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.setFont(document.body_font, 9)
    canvas.drawCentredString(A4[0] / 2, 14 * mm, f"AI Tutor sample - {document.page}")
    canvas.restoreState()


def build_pdf() -> None:
    body_font, bold_font = "Helvetica", "Helvetica-Bold"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=24 * mm,
        leftMargin=24 * mm,
        topMargin=22 * mm,
        bottomMargin=24 * mm,
        title="Linear Algebra Mini-Lesson",
        author="AI Tutor project contributors",
        subject="CC0 PDF ingestion test fixture",
    )
    document.body_font = body_font

    base = getSampleStyleSheet()
    title = ParagraphStyle(
        "FixtureTitle",
        parent=base["Title"],
        fontName=bold_font,
        fontSize=25,
        leading=34,
        textColor=colors.HexColor("#0F172A"),
        alignment=TA_CENTER,
        spaceAfter=12 * mm,
    )
    heading = ParagraphStyle(
        "FixtureHeading",
        parent=base["Heading1"],
        fontName=bold_font,
        fontSize=17,
        leading=24,
        textColor=colors.HexColor("#1D4ED8"),
        spaceAfter=5 * mm,
    )
    body = ParagraphStyle(
        "FixtureBody",
        parent=base["BodyText"],
        fontName=body_font,
        fontSize=11.5,
        leading=20,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4 * mm,
    )
    formula = ParagraphStyle(
        "FixtureFormula",
        parent=body,
        fontName=bold_font,
        fontSize=13,
        leading=21,
        leftIndent=8 * mm,
        borderColor=colors.HexColor("#BFDBFE"),
        borderWidth=1,
        borderPadding=8,
        backColor=colors.HexColor("#EFF6FF"),
        spaceBefore=3 * mm,
        spaceAfter=6 * mm,
    )
    note = ParagraphStyle(
        "FixtureNote",
        parent=body,
        fontSize=9.5,
        leading=16,
        textColor=colors.HexColor("#475569"),
    )

    story = [
        Spacer(1, 12 * mm),
        Paragraph("Linear Algebra Mini-Lesson", title),
        Paragraph("PDF ingestion, search, and page citation fixture", heading),
        Paragraph(
            "This document is a test fixture authored by the AI Tutor project. "
            "It contains no material copied from an external textbook, and its "
            "contents are released under CC0 1.0.",
            body,
        ),
        Spacer(1, 8 * mm),
        Paragraph("1. Vectors and linear combinations", heading),
        Paragraph(
            "A vector can represent a quantity with magnitude and direction, or an "
            "ordered list of numbers. The two-dimensional vector v = (2, 1) can "
            "represent a point or a displacement in the plane.",
            body,
        ),
        Paragraph("The expression a u + b v is a linear combination of u and v.", formula),
        Paragraph(
            "Let u = (1, 0) and v = (0, 1). Then 3u + 2v = (3, 2). By changing "
            "the coefficients, these two vectors can describe different points in "
            "the plane.",
            body,
        ),
        Paragraph(
            "Search verification keyword: cobalt-vector-17. Tests can verify that "
            "this unique phrase appears on page 1.",
            note,
        ),
        PageBreak(),
        Paragraph("2. Matrix-vector multiplication", heading),
        Paragraph(
            "A matrix-vector product can be calculated by taking the dot product "
            "of each matrix row with the vector. It can also be interpreted as a "
            "linear combination of the matrix columns.",
            body,
        ),
        Table(
            [
                ["Matrix A", "Vector x", "Result Ax"],
                ["[[1, 2], [3, 4]]", "[5, 6]", "[17, 39]"],
            ],
            colWidths=[58 * mm, 38 * mm, 38 * mm],
            style=TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), body_font),
                    ("FONTNAME", (0, 0), (-1, 0), bold_font),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DBEAFE")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1E293B")),
                    ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#94A3B8")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            ),
        ),
        Spacer(1, 7 * mm),
        Paragraph(
            "Using the columns, Ax = 5(1, 3) + 6(2, 4) = (17, 39). This view "
            "shows that matrix-vector multiplication is a linear combination.",
            formula,
        ),
        Paragraph(
            "Search verification keyword: amber-matrix-42. A page-aware search "
            "result should cite page 2.",
            note,
        ),
        PageBreak(),
        Paragraph("3. Check your understanding", heading),
        Paragraph("Exercise 1: Given u = (2, 1) and v = (-1, 3), find 2u + v.", body),
        Paragraph(
            "Exercise 2: Given A = [[2, 0], [1, 3]] and x = [4, 2], find Ax.",
            body,
        ),
        Spacer(1, 5 * mm),
        Paragraph("Answers", heading),
        Paragraph("Exercise 1: 2u + v = 2(2, 1) + (-1, 3) = (3, 5).", formula),
        Paragraph("Exercise 2: Ax = [2x4 + 0x2, 1x4 + 3x2] = [8, 10].", formula),
        Paragraph(
            "Search verification keyword: jade-exercise-93. This unique phrase "
            "appears only on page 3.",
            note,
        ),
        Spacer(1, 12 * mm),
        Paragraph(
            "License: CC0 1.0 Universal. Author: AI Tutor project contributors.",
            note,
        ),
    ]

    document.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
