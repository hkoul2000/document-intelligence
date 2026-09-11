from pathlib import Path

from app.services.document_type_service import (
    SUPPORTED_DOCUMENT_TYPES,
    validate_document_type,
)


def test_supported_document_types():
    expected_types = {
        "invoice",
        "balance_sheet",
        "profit_and_loss",
        "cash_flow_statement",
    }

    assert SUPPORTED_DOCUMENT_TYPES == expected_types


def test_valid_document_type():
    result = validate_document_type("balance_sheet")

    assert result["valid"] is True
    assert result["document_type"] == "balance_sheet"


def test_invalid_document_type():
    result = validate_document_type("random_document")

    assert result["valid"] is False


def test_sample_balance_sheet_exists():
    project_root = Path(__file__).resolve().parents[1]

    sample_file = project_root / "sample_balance_sheet.pdf"

    assert sample_file.exists()


def test_sample_invoice_exists():
    project_root = Path(__file__).resolve().parents[1]

    sample_file = project_root / "sample_invoice.pdf"

    assert sample_file.exists()


def test_sample_profit_and_loss_exists():
    project_root = Path(__file__).resolve().parents[1]

    sample_file = project_root / "sample_profit_and_loss.pdf"

    assert sample_file.exists()


def test_sample_cash_flow_statement_exists():
    project_root = Path(__file__).resolve().parents[1]

    sample_file = project_root / "sample_cash_flow_statement.pdf"

    assert sample_file.exists()