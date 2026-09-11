from app.services.extraction_service import extract_document


file_path = "../dataset/Invoices/batch1-1109.jpg"


extracted_data = extract_document(
    file_path=file_path,
    document_type="invoice"
)


print("\n========== INVOICE EXTRACTION ==========\n")
print(extracted_data)