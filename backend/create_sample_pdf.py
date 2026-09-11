from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch


OUTPUT_FILE = "sample_document.pdf"


def create_sample_pdf():
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
        spaceAfter=8,
    )

    story = []

    story.append(
        Paragraph(
            "Document Intelligence Test Document",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "1. Company Information",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "Company Name: OpenAI",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "Industry: Artificial Intelligence",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "Headquarters: San Francisco, California",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "Number of Employees: 500",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "2. Financial Information",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "Annual Revenue: $100 million",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "Annual Operating Expenses: $75 million",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "Operating Profit: $25 million",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "3. Document Purpose",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "This document is created to test the Document Intelligence "
            "document ingestion pipeline. The pipeline should be able to "
            "accept the PDF, extract its native text, normalize the text, "
            "and return the processed content through the FastAPI endpoint.",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "4. Test Statement",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "Document processing is successful when the extracted text "
            "contains the company name, financial information, and the "
            "document purpose described above.",
            body_style,
        )
    )

    document.build(story)

    print(f"Sample PDF created successfully: {OUTPUT_FILE}")


if __name__ == "__main__":
    create_sample_pdf()