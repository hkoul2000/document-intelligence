import io
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image


def extract_text_from_image(image_path: str) -> list[dict]:
    """
    Extract OCR text from a JPG or PNG image.
    """

    image = Image.open(image_path)

    text = pytesseract.image_to_string(image)

    return [
        {
            "page": 1,
            "text": text.strip()
        }
    ]


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Convert every PDF page to an image and extract OCR text.
    """

    pdf = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(pdf, start=1):

        # Convert PDF page to an image at 200 DPI
        pixmap = page.get_pixmap(dpi=200)

        # Convert the image bytes into a PIL image
        image = Image.open(
            io.BytesIO(pixmap.tobytes("png"))
        )

        # Run OCR
        text = pytesseract.image_to_string(image)

        pages.append(
            {
                "page": page_number,
                "text": text.strip()
            }
        )

    pdf.close()

    return pages


def extract_text(file_path: str) -> list[dict]:
    """
    Automatically choose the correct OCR process
    based on the file extension.
    """

    extension = Path(file_path).suffix.lower()

    if extension in [".jpg", ".jpeg", ".png"]:
        return extract_text_from_image(file_path)

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )