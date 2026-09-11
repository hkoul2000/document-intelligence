from app.services.document_type_service import validate_document_type
from app.services.file_validation_service import validate_file
from app.services.ocr_service import extract_text
from app.services.extraction_service import extract_document
from app.services.validation_service import validate_document


def process_document(
    file_path: str,
    document_type: str,
    use_extraction: bool = True
) -> dict:
    """
    Main document-processing pipeline.

    Steps:
    1. Validate the uploaded file.
    2. Validate the document type.
    3. Extract OCR text.
    4. Extract structured data using Gemini.
    5. Run financial validation.

    Parameters
    ----------
    file_path : str
        Path to the uploaded document.

    document_type : str
        One of the supported document types.

    use_extraction : bool
        If True, run Gemini extraction and financial validation.
        If False, stop after OCR. This is useful for local testing
        when the Gemini API is unavailable or quota is exhausted.
    """

    # ---------------------------------------------------------
    # Step 1: Validate file
    # ---------------------------------------------------------

    file_validation = validate_file(file_path)

    if not file_validation["valid"]:
        return {
            "status": "FAILED",
            "stage": "FILE_VALIDATION",
            "file_validation": file_validation,
            "document_type": document_type,
            "extracted_data": None,
            "validation_checks": [],
        }

    # ---------------------------------------------------------
    # Step 2: Validate document type
    # ---------------------------------------------------------

    type_validation = validate_document_type(document_type)

    if not type_validation["valid"]:
        return {
            "status": "FAILED",
            "stage": "DOCUMENT_TYPE_VALIDATION",
            "file_validation": file_validation,
            "document_type_validation": type_validation,
            "document_type": document_type,
            "extracted_data": None,
            "validation_checks": [],
        }

    # ---------------------------------------------------------
    # Step 3: OCR
    # ---------------------------------------------------------

    try:
        ocr_pages = extract_text(file_path)

        ocr_text = "\n\n".join(
            page["text"]
            for page in ocr_pages
        )

    except Exception as exc:
        return {
            "status": "FAILED",
            "stage": "OCR",
            "file_validation": file_validation,
            "document_type_validation": type_validation,
            "document_type": document_type,
            "error": str(exc),
            "extracted_data": None,
            "validation_checks": [],
        }

    # ---------------------------------------------------------
    # Optional OCR-only mode
    # ---------------------------------------------------------

    if not use_extraction:
        return {
            "status": "OCR_COMPLETED",
            "stage": "OCR",
            "file_validation": file_validation,
            "document_type_validation": type_validation,
            "document_type": document_type,
            "ocr_text": ocr_text,
            "extracted_data": None,
            "validation_checks": [],
        }

    # ---------------------------------------------------------
    # Step 4: Structured extraction using Gemini
    # ---------------------------------------------------------

    try:
        extracted_data = extract_document(
            file_path=file_path,
            document_type=document_type
        )

    except Exception as exc:
        return {
            "status": "FAILED",
            "stage": "EXTRACTION",
            "file_validation": file_validation,
            "document_type_validation": type_validation,
            "document_type": document_type,
            "ocr_text": ocr_text,
            "error": str(exc),
            "extracted_data": None,
            "validation_checks": [],
        }

    # ---------------------------------------------------------
    # Step 5: Financial validation
    # ---------------------------------------------------------

    try:
        validation_checks = validate_document(
            document_type=document_type,
            extracted_data=extracted_data
        )

    except Exception as exc:
        return {
            "status": "FAILED",
            "stage": "FINANCIAL_VALIDATION",
            "file_validation": file_validation,
            "document_type_validation": type_validation,
            "document_type": document_type,
            "ocr_text": ocr_text,
            "extracted_data": extracted_data,
            "error": str(exc),
            "validation_checks": [],
        }

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return {
        "status": "COMPLETED",
        "stage": "COMPLETED",
        "file_validation": file_validation,
        "document_type_validation": type_validation,
        "document_type": document_type,
        "ocr_text": ocr_text,
        "extracted_data": extracted_data,
        "validation_checks": validation_checks,
    }