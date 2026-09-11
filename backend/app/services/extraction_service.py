import json
import os

from dotenv import load_dotenv
from google import genai

from app.services.ocr_service import extract_text


def normalize_financial_number(value):
    """
    Convert OCR/Gemini financial number strings into numeric values.

    Examples:
    "3,49" -> 3.49
    "126,27" -> 126.27
    "10%" -> 10.0
    25 -> 25
    None -> None
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        value = value.strip()

        # Remove percentage sign
        value = value.replace("%", "")

        # Convert comma decimal separator to dot
        value = value.replace(",", ".")

        try:
            return float(value)
        except ValueError:
            return value

    return value


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured in the .env file."
    )

client = genai.Client(api_key=api_key)


def extract_document(file_path: str, document_type: str) -> dict:
    """
    Extract structured information from a document using OCR + Gemini.
    """

    # Step 1: Extract text using OCR
    pages = extract_text(file_path)

    ocr_text = "\n\n".join(
        f"PAGE {page['page']}:\n{page['text']}"
        for page in pages
    )

    # Step 2: Select the extraction structure
    # based on the document type

    if document_type == "invoice":

        extraction_structure = """
{
    "invoice_number": {
        "value": null,
        "page": null,
        "evidence": null
    },
    "invoice_date": {
        "value": null,
        "page": null,
        "evidence": null
    },
    "seller": {
        "name": null,
        "address": null,
        "tax_id": null,
        "iban": null
    },
    "client": {
        "name": null,
        "address": null,
        "tax_id": null
    },
    "items": [
        {
            "description": null,
            "quantity": null,
            "unit_price": null,
            "net_value": null,
            "vat_rate": null
        }
    ],
    "vat_rate": null,
    "net_total": null,
    "vat_total": null,
    "gross_total": null
}
"""

    elif document_type == "balance_sheet":

        extraction_structure = """
{
    "statement_date": null,
    "unit": null,
    "periods": [],
    "capital_and_liabilities": {
        "capital": null,
        "employees_stock_options_units_outstanding": null,
        "reserves_and_surplus": null,
        "minority_interest": null,
        "deposits": null,
        "borrowings": null,
        "other_liabilities_and_provisions": null,
        "policyholders_funds": null,
        "total": null
    },
    "assets": {
        "cash_and_balances_with_reserve_bank": null,
        "balances_with_banks_and_money_at_call": null,
        "investments": null,
        "advances": null,
        "fixed_assets": null,
        "other_assets": null,
        "total": null
    },
    "contingent_liabilities": null,
    "bills_for_collection": null
}
"""

    elif document_type == "profit_and_loss":

        extraction_structure = """
{
    "statement_date": null,
    "unit": null,
    "periods": [],
    "income": {
        "interest_earned": null,
        "other_income": null,
        "total_income": null
    },
    "expenditure": {
        "interest_expended": null,
        "operating_expenses": null,
        "provisions_and_contingencies": null,
        "total_expenditure": null
    },
    "profit": {
        "consolidated_net_profit_before_minority_interest": null,
        "minority_interest": null,
        "net_profit_attributable_to_group": null
    },
    "appropriations": {},
    "earnings_per_share": {
        "basic": null,
        "diluted": null
    }
}
"""

    elif document_type == "cash_flow_statement":

        extraction_structure = """
{
    "statement_date": null,
    "unit": null,
    "periods": [
        {
            "period_end_date": null,
            "operating_activities": {
                "net_cash_from_operating_activities": null
            },
            "investing_activities": {
                "net_cash_from_investing_activities": null
            },
            "financing_activities": {
                "net_cash_from_financing_activities": null
            },
            "foreign_exchange_adjustment": null,
            "net_increase_in_cash": null,
            "opening_cash_and_cash_equivalents": null,
            "closing_cash_and_cash_equivalents": null
        }
    ]
}
"""

    else:

        raise ValueError(
            f"Unsupported document type: {document_type}"
        )

    # Step 3: Ask Gemini to extract structured information

    prompt = f"""
You are a document extraction system.

The document type is: {document_type}

The following text was extracted from the document using OCR.

Extract all meaningful information that is explicitly present
in the OCR text.

Do NOT invent, guess, or infer missing information.

If a value is not present or cannot be reliably read,
return null.

For comparative financial statements, preserve each available
period separately.

For important extracted fields, preserve traceability
to the OCR source whenever possible.

When a field has value, page, and evidence fields in the
provided structure:

- Put the extracted value in "value".
- Put the source page number in "page".
- Put the exact or near-exact OCR text supporting the value
  in "evidence".
- If the value cannot be reliably identified, return null
  for the value, page, and evidence fields.

Do not invent evidence.

Return ONLY valid JSON.

Use this structure:

{extraction_structure}

OCR TEXT:
{ocr_text}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    # Step 4: Clean Gemini response

    cleaned_response = response.text.strip()

    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]

    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]

    cleaned_response = cleaned_response.strip()

    # Step 5: Convert JSON string into Python dictionary

    try:
        extracted_data = json.loads(cleaned_response)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Gemini returned invalid JSON: {error}"
        ) from error

    # Step 6: Normalize invoice financial numbers

    if document_type == "invoice":

        for item in extracted_data.get("items", []):

            item["quantity"] = normalize_financial_number(
                item.get("quantity")
            )

            item["unit_price"] = normalize_financial_number(
                item.get("unit_price")
            )

            item["net_value"] = normalize_financial_number(
                item.get("net_value")
            )

            item["vat_rate"] = normalize_financial_number(
                item.get("vat_rate")
            )

        # Normalize fields that contain
        # value/page/evidence

        for field_name in [
            "vat_rate",
            "net_total",
            "vat_total",
            "gross_total",
        ]:

            field = extracted_data.get(field_name)

            if isinstance(field, dict) and "value" in field:

                field["value"] = normalize_financial_number(
                    field.get("value")
                )

    return extracted_data