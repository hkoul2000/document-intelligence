import json
import os
import tempfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.document_repository import (
    create_document,
    get_all_documents,
    get_document_by_id,
    get_document_by_name,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
)
from app.services.chat_service import answer_document_question
from app.services.document_processing_service import process_document


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


@router.post("/process")
async def process_uploaded_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    use_extraction: bool = Form(default=True),
    db: Session = Depends(get_db),
):
    """
    Upload and process a document.

    The uploaded file is temporarily stored on disk and passed
    to the document processing pipeline.

    The processing result is persisted in the database.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file name was provided.",
        )

    # Preserve the original file extension.
    file_extension = os.path.splitext(file.filename)[1]

    temp_file_path = None

    try:
        # Save uploaded file temporarily.
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
        ) as temp_file:

            temp_file_path = temp_file.name

            contents = await file.read()
            temp_file.write(contents)

        # Process document.
        result = process_document(
            file_path=temp_file_path,
            document_type=document_type,
            use_extraction=use_extraction,
        )

        # Persist processing result in database.
        document = create_document(
            db=db,
            document_name=file.filename,
            document_type=document_type,
            status=result.get("status", "UNKNOWN"),
            file_validation=result.get("file_validation"),
            extracted_data=result.get("extracted_data"),
            validation_checks=result.get("validation_checks"),
        )

        # Return result.
        return {
            "document_id": document.id,
            "filename": file.filename,
            "result": result,
        }

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"File processing failed: {str(exc)}",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the document.",
        ) from exc

    finally:
        # Clean up temporary file.
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.get(
    "",
    response_model=DocumentListResponse,
)
def get_documents(
    db: Session = Depends(get_db),
):
    """
    Return all processed documents stored in the database.
    """

    documents = get_all_documents(db)

    return {
        "count": len(documents),
        "documents": [
            {
                "id": document.id,
                "document_name": document.document_name,
                "document_type": document.document_type,
                "status": document.status,
                "created_at": document.created_at,
            }
            for document in documents
        ],
    }


@router.get(
    "/name/{document_name}",
    response_model=DocumentResponse,
)
def get_document_by_filename(
    document_name: str,
    db: Session = Depends(get_db),
):
    """
    Return the most recently processed document with the given filename.
    """

    document = get_document_by_name(
        db=db,
        document_name=document_name,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with name '{document_name}' not found.",
        )

    return {
        "id": document.id,
        "document_name": document.document_name,
        "document_type": document.document_type,
        "status": document.status,
        "file_validation": (
            json.loads(document.file_validation)
            if document.file_validation
            else None
        ),
        "extracted_data": (
            json.loads(document.extracted_data)
            if document.extracted_data
            else None
        ),
        "validation_checks": (
            json.loads(document.validation_checks)
            if document.validation_checks
            else None
        ),
        "created_at": document.created_at,
    }


@router.post(
    "/{document_id}/chat",
    response_model=ChatResponse,
)
def chat_with_document(
    document_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    Ask a question about a processed document.

    The answer is generated using the document's stored
    extracted data and validation results.
    """

    document = get_document_by_id(
        db=db,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {document_id} not found.",
        )

    if document.status != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail="The document has not been successfully processed.",
        )

    try:
        document_data = {
            "id": document.id,
            "document_name": document.document_name,
            "document_type": document.document_type,
            "status": document.status,
            "file_validation": (
                json.loads(document.file_validation)
                if document.file_validation
                else None
            ),
            "extracted_data": (
                json.loads(document.extracted_data)
                if document.extracted_data
                else None
            ),
            "validation_checks": (
                json.loads(document.validation_checks)
                if document.validation_checks
                else None
            ),
        }

        result = answer_document_question(
            question=request.question,
            document=document_data,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate an answer for this document.",
        ) from exc


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    """
    Return a complete processed document by ID.
    """

    document = get_document_by_id(
        db=db,
        document_id=document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document with ID {document_id} not found.",
        )

    return {
        "id": document.id,
        "document_name": document.document_name,
        "document_type": document.document_type,
        "status": document.status,
        "file_validation": (
            json.loads(document.file_validation)
            if document.file_validation
            else None
        ),
        "extracted_data": (
            json.loads(document.extracted_data)
            if document.extracted_data
            else None
        ),
        "validation_checks": (
            json.loads(document.validation_checks)
            if document.validation_checks
            else None
        ),
        "created_at": document.created_at,
    }