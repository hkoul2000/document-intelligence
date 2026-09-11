# Document Intelligence & Financial Validation API 📄🧠

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.108%2B-009688)
![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen)

**Document Intelligence** is an enterprise-grade AI application designed to automate the ingestion, extraction, and validation of unstructured financial documents (Invoices, Receipts, Purchase Orders, and Bank Statements). 

By leveraging modern LLMs (Large Language Models) and OCR technologies, this API eliminates manual data entry and uses a strict rules-engine to mathematically validate extracted financial data.

---

## 📖 Table of Contents
1. [System Architecture & Workflow](#-system-architecture--workflow)
2. [Key Features](#-key-features)
3. [Tech Stack](#-tech-stack)
4. [Project Structure](#-project-structure)
5. [Local Setup & Installation](#-local-setup--installation)
6. [Configuration & Environment Variables](#-configuration)
7. [API Documentation](#-api-documentation)
8. [Financial Validation Rules](#-financial-validation-rules)
9. [Development & Contribution](#-development)

---

## 🏗️ System Architecture & Workflow

How the data flows through the application:
1. **Ingestion (Frontend/API):** Users upload a PDF or Image via the UI or the `/upload` API endpoint.
2. **Text Extraction (OCR):** The backend extracts raw text and spatial layout using tools like PyMuPDF or Tesseract.
3. **AI Parsing (LLM):** The raw text is sent to an AI Model (e.g., Google Gemini) with a strict prompt to extract structured JSON (Merchant Name, Dates, Line Items, Tax, Total).
4. **Validation Engine:** The extracted JSON passes through Python validation scripts ensuring mathematical consistency.
5. **Human-in-the-loop (Dashboard):** The validated (or flagged) data is presented on the Jinja2 Dashboard for final user approval.
6. **Storage:** Finalized data is persisted to an SQL Database.

---

## 🚀 Key Features

### Stage 1: Foundation (Current)
- ✅ **FastAPI Backend:** Asynchronous, high-concurrency REST API.
- ✅ **Jinja2 SSR Dashboard:** Server-side rendered frontend seamlessly integrated into the Python backend.
- ✅ **Static Asset Management:** Configured routing for CSS, JS, and image assets.
- ✅ **Health Monitoring:** Endpoint to monitor system uptime.

### Stage 2: Intelligence Engine (Upcoming)
- ⏳ **Document Upload API:** Secure handling of multipart/form-data.
- ⏳ **LLM Integration:** Connecting to AI provider APIs for intelligent text parsing.
- ⏳ **Mathematical Validation:** Scripts to cross-check extracted numbers.

### Stage 3: Persistence & Review (Upcoming)
- ⏳ **SQLAlchemy ORM:** SQLite/PostgreSQL database integration.
- ⏳ **Data Table UI:** A dashboard view showing extracted documents and their validation status (Pass/Fail).

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | Extremely fast Python web framework. |
| **Server** | [Uvicorn](https://www.uvicorn.org/) | ASGI web server implementation. |
| **Frontend Rendering**| [Jinja2](https://jinja.palletsprojects.com/) | Fast, expressive, extensible templating engine. |
| **Data Validation** | [Pydantic](https://docs.pydantic.dev/) | Data parsing and validation using Python type hints. |

---

## 📂 Project Structure

```text
document-intelligence/
│
├── backend/
│   └── app/
│       ├── main.py           # Application entry point, mounts static/templates, defines routes
│       ├── api/              # (Planned) API endpoint routers (e.g., upload.py, extract.py)
│       ├── core/             # (Planned) Core config, security, and logging settings
│       ├── models/           # (Planned) SQLAlchemy database models
│       ├── schemas/          # (Planned) Pydantic schemas for request/response validation
│       └── services/         # (Planned) Business logic (AI extraction, math validation)
│
├── frontend/
│   ├── static/               
│   │   └── css/
│   │       └── style.css     # UI Styling
│   └── templates/
│       └── dashboard.html    # Main user interface template
│
├── .venv/                    # Isolated Python Environment
└── README.md                 # Project Documentation
```

---

## 💻 Local Setup & Installation

Follow these steps to run the project on your local machine.

### 1. Clone the repository
```bash
git clone <repository-url>
cd document-intelligence
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn jinja2 pydantic
```

---

## ⚙️ Configuration

*(Upcoming Feature)*
The application will utilize a `.env` file at the root directory for sensitive credentials. 
```env
# Example .env file (DO NOT commit to version control)
ENVIRONMENT=development
API_PORT=8000
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./doc_intel.db
```

---

## 🔌 API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, visit:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Current Endpoints

#### `GET /`
- **Description:** Returns the rendered HTML Dashboard.
- **Response:** `200 OK` (text/html)

#### `GET /api/v1/health`
- **Description:** Checks if the API is running correctly.
- **Response:** `200 OK` (application/json)
```json
{
  "status": "healthy",
  "service": "document-intelligence-api"
}
```

---

## 🧮 Financial Validation Rules

The core value of this API is not just extraction, but **validation**. The backend (once fully implemented) will enforce the following rules:

1. **Total Consistency:** `SUM(Line Items) + Tax + Shipping == Grand Total`. If this fails, the document is flagged for manual review.
2. **Date Sanity:** Document dates cannot be in the future.
3. **Currency Normalization:** All detected currencies ($, €, £) are normalized into a standard format.
4. **Confidence Threshold:** If the AI model's confidence for a specific field drops below 85%, the field is highlighted in yellow on the dashboard.

---

## 🧑‍💻 Development

To start the local development server with hot-reloading (automatically restarts when you save a file):

```bash
uvicorn backend.app.main:app --reload --port 8000
```
