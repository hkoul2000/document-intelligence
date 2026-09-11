from PIL import Image
import pytesseract

# Path to the invoice image
image_path = "dataset/Invoices/batch1-1109.jpg"

# Open the image
image = Image.open(image_path)

# Run OCR
text = pytesseract.image_to_string(image)

print("\n========== OCR RESULT ==========\n")
print(text)