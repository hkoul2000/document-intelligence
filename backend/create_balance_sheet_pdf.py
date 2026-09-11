from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


OUTPUT_FILE = "sample_balance_sheet.pdf"


def create_balance_sheet_pdf():
    document = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Heading2"],
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        leading=16,
        spaceAfter=6,
    )

    story = []

    # Title
    story.append(
        Paragraph(
            "ABC Corporation",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Balance Sheet",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            "As of March 31, 2026",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "Unit: USD",
            body_style,
        )
    )

    story.append(Spacer(1, 10))

    # Capital and Liabilities
    story.append(
        Paragraph(
            "Capital and Liabilities",
            heading_style,
        )
    )

    capital_and_liabilities = [
        "Capital: $50,000",
        "Reserves and Surplus: $20,000",
        "Borrowings: $30,000",
        "Other Liabilities and Provisions: $10,000",
        "Total Capital and Liabilities: $110,000",
    ]

    for item in capital_and_liabilities:
        story.append(
            Paragraph(
                item,
                body_style,
            )
        )

    # Assets
    story.append(
        Paragraph(
            "Assets",
            heading_style,
        )
    )

    assets = [
        "Cash and Balances with Reserve Bank: $20,000",
        "Investments: $30,000",
        "Advances: $40,000",
        "Fixed Assets: $10,000",
        "Other Assets: $10,000",
        "Total Assets: $110,000",
    ]

    for item in assets:
        story.append(
            Paragraph(
                item,
                body_style,
            )
        )

    # Contingent Liabilities
    story.append(
        Paragraph(
            "Contingent Liabilities",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "Contingent Liabilities: $5,000",
            body_style,
        )
    )

    # Bills for Collection
    story.append(
        Paragraph(
            "Bills for Collection",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "Bills for Collection: $2,000",
            body_style,
        )
    )

    # Accounting Check
    story.append(
        Paragraph(
            "Accounting Check",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "Total Capital and Liabilities = Total Assets = $110,000",
            body_style,
        )
    )

    document.build(story)

    print(
        f"Balance sheet PDF created successfully: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    create_balance_sheet_pdf()