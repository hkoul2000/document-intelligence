import pymupdf
import pytesseract
from PIL import Image
import io

# Path to the Profit & Loss PDF
pdf_path = "dataset/Profit & Loss/Consolidated Profit & Loss 2026.pdf"

# Open the PDF
pdf = pymupdf.open(pdf_path)

# Process the first page
page = pdf[0]

# Convert PDF page to image
pix = page.get_pixmap(dpi=200)

# Convert image data to PIL image
image = Image.open(io.BytesIO(pix.tobytes("png")))

# Run OCR
text = pytesseract.image_to_string(image)

print("\n========== PROFIT & LOSS OCR ==========\n")
print(text)

pdf.close()