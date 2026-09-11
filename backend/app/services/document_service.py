from app.services.document_processing_service import process_document


def process_uploaded_document(
    file_path: str,
    document_type: str,
) -> dict:
    """
    Process an uploaded document through the complete
    document intelligence pipeline.
    """

    return process_document(
        file_path=file_path,
        document_type=document_type,
        use_extraction=True,
    )