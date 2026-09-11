import os
import json
from urllib.parse import quote_plus

import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "document" not in st.session_state:
    st.session_state.document = None

if "selected_document_id" not in st.session_state:
    st.session_state.selected_document_id = None

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if "gemini_answer" not in st.session_state:
    st.session_state.gemini_answer = None

if "gemini_failed" not in st.session_state:
    st.session_state.gemini_failed = False


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-left: 4rem;
        padding-right: 4rem;
        padding-bottom: 4rem;
    }

    section[data-testid="stSidebar"] {
        background-color: #f1f3f7;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API HEALTH
# ============================================================

def check_api_health():

    try:

        response = requests.get(
            f"{API_BASE_URL}/api/v1/health",
            timeout=5,
        )

        return response.status_code == 200

    except requests.RequestException:

        return False


# ============================================================
# GET ALL DOCUMENTS
# ============================================================

def get_documents():

    try:

        response = requests.get(
            f"{API_BASE_URL}/api/v1/documents",
            timeout=15,
        )

        if response.status_code != 200:
            return []

        data = response.json()

        if isinstance(data, dict):

            documents = data.get(
                "documents",
                [],
            )

            if isinstance(
                documents,
                list,
            ):
                return documents

        if isinstance(
            data,
            list,
        ):
            return data

        return []

    except Exception:

        return []


# ============================================================
# GET SINGLE DOCUMENT
# ============================================================

def get_document(document_id):

    if document_id is None:
        return None

    try:

        response = requests.get(
            f"{API_BASE_URL}/api/v1/documents/{document_id}",
            timeout=30,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if isinstance(
            data,
            dict,
        ):
            return data

        return None

    except Exception:

        return None


# ============================================================
# PROCESS DOCUMENT
# ============================================================

def process_document(
    uploaded_file,
    document_type,
):

    try:

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "application/pdf",
            )
        }

        form_data = {
            "document_type": document_type,
        }

        response = requests.post(
            f"{API_BASE_URL}/api/v1/documents/process",
            files=files,
            data=form_data,
            timeout=300,
        )

        return response

    except requests.RequestException as exc:

        return None, str(exc)


# ============================================================
# ASK GEMINI
# ============================================================

def ask_gemini(
    document_id,
    question,
):

    try:

        response = requests.post(
            f"{API_BASE_URL}/api/v1/documents/"
            f"{document_id}/chat",
            json={
                "question": question,
            },
            timeout=120,
        )

        return response

    except requests.Timeout:

        return None, "Gemini request timed out."

    except requests.RequestException as exc:

        return None, str(exc)


# ============================================================
# GET PROCESSED DOCUMENT
# ============================================================

def get_processed_document(
    response_data,
):

    if not isinstance(
        response_data,
        dict,
    ):
        return None

    document_id = response_data.get(
        "id"
    )

    if document_id is None:

        document_id = response_data.get(
            "document_id"
        )

    if document_id is None:

        result = response_data.get(
            "result"
        )

        if isinstance(
            result,
            dict,
        ):

            document_id = result.get(
                "id"
            )

    if document_id is None:
        return None

    return get_document(
        document_id
    )


# ============================================================
# PARSE JSON SAFELY
# ============================================================

def parse_json_value(value):

    if isinstance(
        value,
        str,
    ):

        try:

            return json.loads(
                value
            )

        except Exception:

            return None

    return value


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header(
    "Document Processing"
)


document_type = st.sidebar.selectbox(
    "Document Type",
    [
        "invoice",
        "balance_sheet",
        "profit_and_loss",
        "cash_flow_statement",
    ],
)


uploaded_file = st.sidebar.file_uploader(
    "Upload PDF Document",
    type=["pdf"],
)


process_button = st.sidebar.button(
    "Process Document",
    type="primary",
    use_container_width=True,
)


# ============================================================
# API STATUS
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader(
    "API Status"
)


api_online = check_api_health()


if api_online:

    st.sidebar.success(
        "API: Online"
    )

else:

    st.sidebar.error(
        "API: Offline"
    )


# ============================================================
# PREVIOUSLY PROCESSED DOCUMENTS
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader(
    "Previously Processed Documents"
)


documents = get_documents()


completed_documents = []


for item in documents:

    if not isinstance(
        item,
        dict,
    ):
        continue

    status = str(
        item.get(
            "status",
            "",
        )
    ).upper()


    if status == "COMPLETED":

        completed_documents.append(
            item
        )


if completed_documents:

    document_options = {}


    for item in completed_documents:

        item_id = item.get(
            "id"
        )

        item_name = item.get(
            "document_name",
            "Unknown Document",
        )

        item_type = item.get(
            "document_type",
            "unknown",
        )


        label = (
            f"{item_name} "
            f"({item_type})"
        )


        document_options[
            label
        ] = item_id


    selected_label = st.sidebar.selectbox(
        "Select processed document",
        list(
            document_options.keys()
        ),
    )


    load_button = st.sidebar.button(
        "Load Document",
        use_container_width=True,
    )


    if load_button:

        selected_id = document_options[
            selected_label
        ]


        with st.spinner(
            "Loading document..."
        ):

            loaded_document = get_document(
                selected_id
            )


        if isinstance(
            loaded_document,
            dict,
        ):

            st.session_state.document = (
                loaded_document
            )

            st.session_state.selected_document_id = (
                selected_id
            )

            st.session_state.last_question = ""
            st.session_state.gemini_answer = None
            st.session_state.gemini_failed = False

            st.rerun()


        else:

            st.sidebar.error(
                "Unable to load document."
            )


else:

    st.sidebar.info(
        "No completed documents available."
    )


# ============================================================
# PROJECT HEADING
# ============================================================

st.title(
    "📄 Document Intelligence"
)


st.caption(
    "AI-powered document ingestion, extraction, "
    "financial validation, and Q&A"
)


# ============================================================
# CURRENT DOCUMENT
# ============================================================

document = st.session_state.get(
    "document"
)


# ============================================================
# LANDING PAGE
# ============================================================

if not isinstance(
    document,
    dict,
):

    st.info(
        "👉 Upload a PDF from the sidebar and click "
        "**Process Document** to begin."
    )


    st.markdown(
        "## What this application can do"
    )


    st.markdown(
        """
        - 📄 Validate uploaded documents
        - 🔎 Extract text using OCR
        - 🧠 Extract structured financial information
        - ✅ Perform financial validation checks
        - 💾 Persist processed documents
        - 💬 Answer questions about processed documents
        """
    )


    st.markdown(
        "## Supported documents"
    )


    st.markdown(
        """
        - Invoice
        - Balance Sheet
        - Profit & Loss Statement
        - Cash Flow Statement
        """
    )


# ============================================================
# PROCESS DOCUMENT
# ============================================================

if process_button:

    if uploaded_file is None:

        st.warning(
            "Please upload a PDF document first."
        )


    elif not api_online:

        st.error(
            "The FastAPI backend is unavailable."
        )


    else:

        with st.spinner(
            "Processing document..."
        ):

            result = process_document(
                uploaded_file,
                document_type,
            )


        if isinstance(
            result,
            tuple,
        ):

            st.error(
                "Unable to connect to FastAPI."
            )

            st.caption(
                result[1]
            )


        else:

            response = result


            if response.status_code == 200:

                try:

                    response_data = response.json()

                except ValueError:

                    response_data = {}


                loaded_document = (
                    get_processed_document(
                        response_data
                    )
                )


                if isinstance(
                    loaded_document,
                    dict,
                ):

                    st.session_state.document = (
                        loaded_document
                    )

                    st.session_state.selected_document_id = (
                        loaded_document.get(
                            "id"
                        )
                    )

                    st.session_state.last_question = ""
                    st.session_state.gemini_answer = None
                    st.session_state.gemini_failed = False

                    st.success(
                        "Document processed successfully."
                    )

                    st.rerun()


                else:

                    st.error(
                        "Document was processed, but "
                        "the processed result could not be loaded."
                    )


            else:

                try:

                    error_data = response.json()

                except ValueError:

                    error_data = {}


                detail = error_data.get(
                    "detail",
                    "Unknown processing error.",
                )


                st.error(
                    "Document processing failed."
                )


                if isinstance(
                    detail,
                    dict,
                ):

                    st.warning(
                        f"Stage: "
                        f"{detail.get('stage', 'UNKNOWN')}"
                    )

                    st.error(
                        f"Error: "
                        f"{detail.get('error', 'Unknown error')}"
                    )

                else:

                    st.warning(
                        str(detail)
                    )


# ============================================================
# RELOAD DOCUMENT
# ============================================================

document = st.session_state.get(
    "document"
)


# ============================================================
# LOADED DOCUMENT
# ============================================================

if isinstance(
    document,
    dict,
):

    document_id = document.get(
        "id",
        "N/A",
    )


    document_name = document.get(
        "document_name",
        "Unknown Document",
    )


    document_type_value = document.get(
        "document_type",
        "Unknown",
    )


    document_status = document.get(
        "status",
        "Unknown",
    )


    created_at = document.get(
        "created_at",
        "N/A",
    )


    # ========================================================
    # DOCUMENT TITLE
    # ========================================================

    st.divider()


    st.subheader(
        f"📑 {document_name}"
    )


    st.caption(
        f"Processed "
        f"{document_type_value.replace('_', ' ').title()} "
        f"document"
    )


    # ========================================================
    # DOCUMENT SUMMARY
    # ========================================================

    st.markdown(
        "## 📋 Document Summary"
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        with st.container(
            border=True,
        ):

            st.caption(
                "Document ID"
            )

            st.subheader(
                str(document_id)
            )


    with col2:

        with st.container(
            border=True,
        ):

            st.caption(
                "Document Type"
            )

            st.subheader(
                document_type_value
                .replace(
                    "_",
                    " ",
                )
                .title()
            )


    with col3:

        with st.container(
            border=True,
        ):

            st.caption(
                "Processing Status"
            )


            if str(
                document_status
            ).upper() == "COMPLETED":

                st.success(
                    "✅ COMPLETED"
                )

            else:

                st.error(
                    f"⚠️ {document_status}"
                )


    with col4:

        with st.container(
            border=True,
        ):

            st.caption(
                "Processed Date"
            )

            st.subheader(
                str(created_at)[:10]
            )


    # ========================================================
    # FILE VALIDATION
    # ========================================================

    st.markdown(
        "## 📁 File Validation"
    )


    file_validation = parse_json_value(
        document.get(
            "file_validation"
        )
    )


    if isinstance(
        file_validation,
        dict,
    ):

        valid = file_validation.get(
            "valid"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            if valid is True:

                st.success(
                    "✅ File is valid"
                )

            elif valid is False:

                st.error(
                    "❌ File is invalid"
                )

            else:

                st.info(
                    "Validation unavailable"
                )


        with col2:

            st.metric(
                "File Type",
                file_validation.get(
                    "file_type",
                    "N/A",
                ),
            )


        with col3:

            st.metric(
                "Page Count",
                file_validation.get(
                    "page_count",
                    "N/A",
                ),
            )


    else:

        st.info(
            "File validation information is unavailable."
        )


    # ========================================================
    # DOCUMENT TYPE VALIDATION
    # ========================================================

    st.markdown(
        "## 🗂️ Document Type Validation"
    )


    st.success(
        f"✅ Detected document type: "
        f"**{document_type_value.replace('_', ' ').title()}**"
    )


    # ========================================================
    # FINANCIAL VALIDATION
    # ========================================================

    st.markdown(
        "## 📊 Financial Validation"
    )


    validation_checks = parse_json_value(
        document.get(
            "validation_checks"
        )
    )


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Only meaningful PASS / FAIL checks are displayed.
    #
    # NOT_APPLICABLE checks are intentionally hidden.
    # --------------------------------------------------------

    meaningful_checks = []


    if isinstance(
        validation_checks,
        list,
    ):

        for index, check in enumerate(
            validation_checks,
            start=1,
        ):

            if not isinstance(
                check,
                dict,
            ):
                continue


            check_status = str(
                check.get(
                    "status",
                    "",
                )
            ).strip().upper()


            # Hide NOT_APPLICABLE checks
            if check_status in {
                "",
                "NOT_APPLICABLE",
                "N/A",
                "NA",
                "NOT APPLICABLE",
            }:

                continue


            # Only show PASS and FAIL
            if check_status not in {
                "PASS",
                "FAIL",
            }:

                continue


            check_name = check.get(
                "check",
                check.get(
                    "name",
                    f"Validation Check {index}",
                ),
            )


            meaningful_checks.append(
                (
                    check_name,
                    check_status,
                    check.get(
                        "details",
                        "",
                    ),
                )
            )


    if meaningful_checks:

        for (
            check_name,
            check_status,
            details,
        ) in meaningful_checks:


            if check_status == "PASS":

                st.success(
                    f"✅ {check_name} — PASS"
                )


            elif check_status == "FAIL":

                st.error(
                    f"❌ {check_name} — FAIL"
                )


            if details:

                st.caption(
                    str(details)
                )


    else:

        st.info(
            "No applicable financial validation checks "
            "are available for this document."
        )


    # ========================================================
    # OCR TEXT
    # ========================================================

    ocr_text = document.get(
        "ocr_text"
    )


    if ocr_text:

        st.markdown(
            "## 🔎 Extracted Text"
        )


        with st.expander(
            "View OCR text"
        ):

            st.text(
                ocr_text
            )


    # ========================================================
    # IMPORTANT:
    #
    # extracted_data is intentionally NOT displayed.
    #
    # It remains in the backend/database and is used
    # by the document Q&A service.
    #
    # ========================================================


    # ========================================================
    # ASK QUESTIONS
    # ========================================================

    st.divider()


    st.markdown(
        "## 💬 Ask Questions About This Document"
    )


    st.caption(
        "Ask Gemini questions using the information "
        "extracted from this document."
    )


    question = st.text_input(
        "Your question",
        placeholder=(
            "Example: What is the invoice number?"
        ),
        key="document_question",
    )


    # ========================================================
    # ASK GEMINI BUTTON
    # ========================================================

    ask_button = st.button(
        "🤖 Ask Gemini",
        type="primary",
        key="ask_gemini_button",
    )


    # ========================================================
    # ASK GEMINI ACTION
    # ========================================================

    if ask_button:

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

            st.session_state.gemini_answer = None
            st.session_state.gemini_failed = False


        else:

            current_document = (
                st.session_state.get(
                    "document"
                )
            )


            if not isinstance(
                current_document,
                dict,
            ):

                st.error(
                    "No processed document is currently loaded."
                )

                st.session_state.gemini_failed = True

                st.session_state.last_question = (
                    question
                )


            else:

                current_document_id = (
                    current_document.get(
                        "id"
                    )
                )


                if current_document_id is None:

                    st.error(
                        "Document ID is missing."
                    )

                    st.session_state.gemini_failed = True

                    st.session_state.last_question = (
                        question
                    )


                else:

                    st.session_state.last_question = (
                        question
                    )

                    st.session_state.gemini_answer = None
                    st.session_state.gemini_failed = False


                    with st.spinner(
                        "Gemini is analyzing the document..."
                    ):

                        response = ask_gemini(
                            current_document_id,
                            question,
                        )


                    # ----------------------------------------
                    # REQUEST FAILURE
                    # ----------------------------------------

                    if isinstance(
                        response,
                        tuple,
                    ):

                        st.session_state.gemini_failed = True

                        st.error(
                            "Gemini could not answer the question."
                        )


                    # ----------------------------------------
                    # SUCCESS
                    # ----------------------------------------

                    elif response.status_code == 200:

                        try:

                            answer_data = response.json()

                        except ValueError:

                            answer_data = {}


                        answer = answer_data.get(
                            "answer"
                        )


                        if (
                            isinstance(
                                answer,
                                str,
                            )
                            and answer.strip()
                        ):

                            st.session_state.gemini_answer = (
                                answer.strip()
                            )

                            st.session_state.gemini_failed = (
                                False
                            )


                        else:

                            st.session_state.gemini_failed = True

                            st.error(
                                "Gemini did not return an answer."
                            )


                    # ----------------------------------------
                    # GEMINI ERROR
                    # ----------------------------------------

                    else:

                        st.session_state.gemini_failed = True

                        st.error(
                            "Gemini could not answer the question."
                        )


    # ========================================================
    # GEMINI ANSWER
    # ========================================================

    if st.session_state.get(
        "gemini_answer"
    ):

        st.markdown(
            "### 🤖 Gemini Answer"
        )


        with st.container(
            border=True,
        ):

            st.write(
                st.session_state.gemini_answer
            )


    # ========================================================
    # ALTERNATIVE AI LINKS
    # ========================================================

    st.markdown(
        "### 🌐 Ask Using Another AI"
    )


    st.caption(
        "Use the same question with another AI service."
    )


    fallback_question = (
        question.strip()
        if question.strip()
        else st.session_state.get(
            "last_question",
            "",
        ).strip()
    )


    if fallback_question:

        encoded_question = quote_plus(
            fallback_question
        )


        google_url = (
            "https://www.google.com/search?q="
            + encoded_question
        )


        chatgpt_url = (
            "https://chatgpt.com/?q="
            + encoded_question
        )


        claude_url = (
            "https://claude.ai/new?q="
            + encoded_question
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.link_button(
                "🔎 Ask Google",
                google_url,
                use_container_width=True,
            )


        with col2:

            st.link_button(
                "🤖 Ask ChatGPT",
                chatgpt_url,
                use_container_width=True,
            )


        with col3:

            st.link_button(
                "✨ Ask Claude",
                claude_url,
                use_container_width=True,
            )


    else:

        st.info(
            "Enter a question above to enable "
            "the Google, ChatGPT, and Claude links."
        )


    # ========================================================
    # EXAMPLE QUESTIONS
    # ========================================================

    st.divider()


    st.markdown(
        "## 💡 Example Questions You Can Ask Gemini"
    )


    st.caption(
        "Try these questions with your processed document."
    )


    current_type = document.get(
        "document_type",
        "",
    )


    if current_type == "invoice":

        examples = [
            "What is the invoice number?",
            "What is the invoice date?",
            "Who is the seller?",
            "What is the net total?",
            "What is the VAT amount?",
            "What is the gross total?",
            "What are the line items in this invoice?",
            "Does the gross total equal the net total plus VAT?",
        ]


    elif current_type == "balance_sheet":

        examples = [
            "What are the total assets?",
            "What is the total capital and liabilities?",
            "What is the total capital?",
            "What are the total liabilities?",
            "Does the balance sheet balance?",
            "What is the balance sheet variance?",
            "Did the financial validation checks pass?",
            "Are total assets equal to capital and liabilities?",
        ]


    elif current_type == "profit_and_loss":

        examples = [
            "What is the net profit?",
            "What are the operating expenses?",
            "What is the interest expense?",
            "What is the revenue?",
            "What is the gross profit?",
            "What is the operating profit?",
            "What is the profit before tax?",
            "Summarize the profit and loss statement.",
        ]


    elif current_type == "cash_flow_statement":

        examples = [
            "What is the operating cash flow?",
            "What is the investing cash flow?",
            "What is the financing cash flow?",
            "What is the net increase in cash?",
            "What is the opening cash balance?",
            "What is the closing cash balance?",
            "What is the statement date?",
            "How much cash was generated from operating activities?",
            "What caused the change in cash?",
            "Does the cash flow statement reconcile?",
        ]


    else:

        examples = [
            "What are the key financial figures?",
            "What information is available in this document?",
            "Are there any validation issues?",
            "Summarize this document.",
        ]


    for index, example in enumerate(
        examples,
        start=1,
    ):

        st.markdown(
            f"**{index}.** {example}"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()


st.caption(
    "Document Intelligence • "
    "AI-powered document ingestion, financial validation, "
    "and document-grounded Q&A"
)