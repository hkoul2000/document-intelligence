import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
)

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured in the .env file."
    )

client = genai.Client(
    api_key=API_KEY
)


def _get_extracted_data(document: dict) -> dict:
    extracted_data = document.get("extracted_data")

    if not extracted_data:
        return {}

    if isinstance(extracted_data, str):
        try:
            return json.loads(extracted_data)
        except json.JSONDecodeError:
            return {}

    return extracted_data


def answer_document_question(
    question: str,
    document: dict,
):
    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    extracted_data = _get_extracted_data(document)

    if not extracted_data:
        raise ValueError(
            "No extracted document data is available."
        )

    document_context = {
        "document_name": document.get(
            "document_name"
        ),
        "document_type": document.get(
            "document_type"
        ),
        "extracted_data": extracted_data,
        "validation_checks": document.get(
            "validation_checks"
        ),
    }

    prompt = f"""
You are a financial document intelligence assistant.

Answer the user's question using ONLY the information
contained in the supplied processed document.

IMPORTANT RULES:

1. Do not invent financial values.
2. Do not use outside information.
3. If the requested information is not present,
   clearly say that it is not available in the document.
4. Use the exact values from the document.
5. Keep the answer concise and professional.
6. For financial amounts, preserve the document's
   currency.
7. If the question asks whether a financial validation
   check passed, use the supplied validation_checks.
8. If calculations are necessary, calculate them only
   from values contained in the document.

DOCUMENT:

{json.dumps(
    document_context,
    indent=2,
    default=str,
)}

USER QUESTION:

{question}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        answer = response.text.strip()

        if not answer:
            answer = (
                "I could not generate an answer from "
                "the available document data."
            )

        return {
            "question": question,
            "answer": answer,
            "document_id": document["id"],
            "document_name": document[
                "document_name"
            ],
        }

    except Exception as exc:
        error_text = str(exc)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text.upper()
            or "QUOTA" in error_text.upper()
        ):
            return {
                "question": question,
                "answer": (
                    "The Gemini API quota for this API key "
                    "has been exhausted. Please use a key "
                    "with available Gemini quota."
                ),
                "document_id": document["id"],
                "document_name": document[
                    "document_name"
                ],
            }

        raise RuntimeError(
            f"Gemini API request failed: {error_text}"
        ) from exc