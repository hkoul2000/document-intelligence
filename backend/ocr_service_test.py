from app.services.ocr_service import extract_text


file_path = "dataset/Invoices/batch1-1109.jpg"

pages = extract_text(file_path)

for page in pages:
    print(f"\n========== PAGE {page['page']} ==========\n")
    print(page["text"])