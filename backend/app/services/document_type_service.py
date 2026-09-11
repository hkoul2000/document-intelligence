SUPPORTED_DOCUMENT_TYPES = {
    "invoice",
    "balance_sheet",
    "profit_and_loss",
    "cash_flow_statement",
}


def validate_document_type(document_type: str) -> dict:
    """
    Validate that the requested document type
    is supported by the system.
    """

    if not document_type:
        return {
            "valid": False,
            "error": "Document type is required.",
        }

    if document_type not in SUPPORTED_DOCUMENT_TYPES:
        return {
            "valid": False,
            "error": (
                f"Unsupported document type: {document_type}"
            ),
        }

    return {
        "valid": True,
        "document_type": document_type,
    }