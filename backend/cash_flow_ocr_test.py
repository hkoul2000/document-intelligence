import pymupdf
import pytesseract
from PIL import Image
import io

# Path to the Cash Flow PDF
pdf_path = "dataset/Cash Flows/Consolidated Cash Flow Statement 2026.pdf"

# Open the PDF
pdf = pymupdf.open(pdf_path)

# Process every page
for page_number, page in enumerate(pdf, start=1):

    print(f"\n========== CASH FLOW - PAGE {page_number} ==========\n")

    # Convert PDF page to image
    pix = page.get_pixmap(dpi=200)

    # Convert image data to PIL image
    image = Image.open(io.BytesIO(pix.tobytes("png")))

    # Run OCR
    text = pytesseract.image_to_string(image)

    print(text)

pdf.close()