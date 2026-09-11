import json

from sqlalchemy.orm import Session

from app.models.models import Document


def create_document(
    db: Session,
    document_name: str,
    document_type: str,
    status: str,
    file_validation: dict | None = None,
    extracted_data: dict | None = None,
    validation_checks: list | None = None,
) -> Document:
    document = Document(
        document_name=document_name,
        document_type=document_type,
        status=status,
        file_validation=json.dumps(file_validation)
        if file_validation is not None
        else None,
        extracted_data=json.dumps(extracted_data)
        if extracted_data is not None
        else None,
        validation_checks=json.dumps(validation_checks)
        if validation_checks is not None
        else None,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_document_by_name(
    db: Session,
    document_name: str,
) -> Document | None:
    return (
        db.query(Document)
        .filter(Document.document_name == document_name)
        .order_by(Document.created_at.desc())
        .first()
    )


def get_document_by_id(
    db: Session,
    document_id: int,
) -> Document | None:
    return (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )


def get_all_documents(
    db: Session,
) -> list[Document]:
    return (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )