from app.services.ocr_service import extract_text


file_path = "dataset/Balance Sheet/Consolidated Balance Sheet 2026.pdf"

pages = extract_text(file_path)

for page in pages:
    print(f"\n========== PAGE {page['page']} ==========\n")
    print(page["text"])