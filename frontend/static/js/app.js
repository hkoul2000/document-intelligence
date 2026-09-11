const API_BASE = "https://document-intelligence-3f3e.onrender.com/api/v1";

const uploadForm = document.getElementById("uploadForm");
const documentType = document.getElementById("documentType");
const fileInput = document.getElementById("fileInput");
const processButton = document.getElementById("processButton");

const filePreview = document.getElementById("filePreview");
const fileName = document.getElementById("fileName");

const processingMessage = document.getElementById("processingMessage");
const errorMessage = document.getElementById("errorMessage");
const successMessage = document.getElementById("successMessage");

const documentsContainer = document.getElementById("documentsContainer");
const refreshButton = document.getElementById("refreshButton");

const resultSection = document.getElementById("resultSection");
const closeResultButton = document.getElementById("closeResultButton");

const resultDocumentName = document.getElementById("resultDocumentName");   
const resultDocumentType = document.getElementById("resultDocumentType");
const resultStatus = document.getElementById("resultStatus");
const resultCreatedAt = document.getElementById("resultCreatedAt");

const extractedData = document.getElementById("extractedData");
const validationData = document.getElementById("validationData");
const rawJson = document.getElementById("rawJson");
const copyJsonButton = document.getElementById("copyJsonButton");

const apiStatusDot = document.getElementById("apiStatusDot");
const apiStatusText = document.getElementById("apiStatusText");


// ---------------------------------------------------------
// Utility functions
// ---------------------------------------------------------

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function formatDocumentType(type) {
    if (!type) {
        return "-";
    }

    return type
        .replace(/_/g, " ")
        .replace(/\b\w/g, letter => letter.toUpperCase());
}


function formatDate(value) {
    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}


function showElement(element) {
    element.classList.remove("hidden");
}


function hideElement(element) {
    element.classList.add("hidden");
}


function showError(message) {
    errorMessage.textContent = message;
    showElement(errorMessage);
}


function showSuccess(message) {
    successMessage.textContent = message;
    showElement(successMessage);
}


function clearMessages() {
    hideElement(errorMessage);
    hideElement(successMessage);
}


// ---------------------------------------------------------
// API health check
// ---------------------------------------------------------

async function checkApiHealth() {

    try {

        const response = await fetch(`${API_BASE}/health`);

        if (!response.ok) {
            throw new Error("API is not healthy");
        }

        const data = await response.json();

        if (data.status === "healthy") {
            apiStatusDot.classList.add("online");
            apiStatusText.textContent = "API Online";
        } else {
            throw new Error("Unexpected health response");
        }

    } catch (error) {

        apiStatusDot.classList.remove("online");
        apiStatusText.textContent = "API Offline";

        console.error("API health check failed:", error);
    }
}


// ---------------------------------------------------------
// File selection
// ---------------------------------------------------------

fileInput.addEventListener("change", () => {

    const file = fileInput.files[0];

    if (!file) {
        fileName.textContent = "No file selected";
        filePreview.classList.remove("has-file");
        return;
    }

    fileName.textContent =
        `${file.name} (${formatFileSize(file.size)})`;

    filePreview.classList.add("has-file");
});


function formatFileSize(bytes) {

    if (bytes === 0) {
        return "0 Bytes";
    }

    const units = [
        "Bytes",
        "KB",
        "MB",
        "GB"
    ];

    const index =
        Math.floor(Math.log(bytes) / Math.log(1024));

    return `${(bytes / Math.pow(1024, index)).toFixed(2)} ${units[index]}`;
}


// ---------------------------------------------------------
// Upload and process document
// ---------------------------------------------------------

uploadForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    clearMessages();

    const file = fileInput.files[0];
    const type = documentType.value;

    if (!type) {
        showError("Please select a document type.");
        return;
    }

    if (!file) {
        showError("Please select a document file.");
        return;
    }


    const allowedTypes = [
        "application/pdf",
        "image/jpeg",
        "image/png"
    ];

    if (!allowedTypes.includes(file.type)) {
        showError(
            "Unsupported file type. Please upload a PDF, JPG, JPEG, or PNG file."
        );
        return;
    }


    const formData = new FormData();

    formData.append("file", file);
    formData.append("document_type", type);
    formData.append("use_extraction", "true");


    processButton.disabled = true;
    processButton.textContent = "Processing...";

    showElement(processingMessage);


    try {

        const response = await fetch(
            `${API_BASE}/documents/process`,
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        if (!response.ok) {

            const errorMessage =
                data.detail ||
                data.message ||
                "Document processing failed.";

            throw new Error(errorMessage);
        }


        hideElement(processingMessage);

        showSuccess(
            `Document processed successfully. Document ID: ${data.document_id}`
        );


        // Reset upload form
        uploadForm.reset();

        fileName.textContent = "No file selected";
        filePreview.classList.remove("has-file");


        // Refresh dashboard
        await loadDocuments();


        // Open processed result
        await loadDocument(data.document_id);


    } catch (error) {

        hideElement(processingMessage);

        showError(
            error.message ||
            "An unexpected error occurred while processing the document."
        );

        console.error("Document processing error:", error);

    } finally {

        processButton.disabled = false;
        processButton.textContent = "Process Document";
    }
});


// ---------------------------------------------------------
// Load processed documents
// ---------------------------------------------------------

async function loadDocuments() {

    documentsContainer.innerHTML =
        `<div class="loading">Loading documents...</div>`;


    try {

        const response =
            await fetch(`${API_BASE}/documents`);


        if (!response.ok) {
            throw new Error("Unable to load processed documents.");
        }


        const data = await response.json();


        if (!data.documents || data.documents.length === 0) {

            documentsContainer.innerHTML = `
                <div class="empty-state">
                    <h3>No processed documents</h3>
                    <p>Upload a document above to get started.</p>
                </div>
            `;

            return;
        }


        renderDocuments(data.documents);


    } catch (error) {

        documentsContainer.innerHTML = `
            <div class="empty-state error-state">
                <h3>Unable to load documents</h3>
                <p>${escapeHtml(error.message)}</p>
            </div>
        `;

        console.error("Dashboard error:", error);
    }
}


// ---------------------------------------------------------
// Render dashboard
// ---------------------------------------------------------

function renderDocuments(documents) {

    const table = document.createElement("table");

    table.className = "documents-table";


    table.innerHTML = `
        <thead>
            <tr>
                <th>Document Name</th>
                <th>Type</th>
                <th>Status</th>
                <th>Processed Time</th>
                <th>Action</th>
            </tr>
        </thead>

        <tbody>
            ${documents.map(document => `

                <tr>

                    <td>
                        <strong>
                            ${escapeHtml(document.document_name)}
                        </strong>
                    </td>

                    <td>
                        ${escapeHtml(
                            formatDocumentType(document.document_type)
                        )}
                    </td>

                    <td>
                        <span class="status-badge ${getStatusClass(document.status)}">
                            ${escapeHtml(document.status)}
                        </span>
                    </td>

                    <td>
                        ${escapeHtml(
                            formatDate(document.created_at)
                        )}
                    </td>

                    <td>
                        <button
                            class="view-button"
                            onclick="loadDocument(${document.id})"
                        >
                            View
                        </button>
                    </td>

                </tr>

            `).join("")}
        </tbody>
    `;


    documentsContainer.innerHTML = "";
    documentsContainer.appendChild(table);
}


function getStatusClass(status) {

    if (!status) {
        return "";
    }

    const normalized =
        status.toLowerCase();

    if (normalized === "completed") {
        return "status-completed";
    }

    if (
        normalized === "failed" ||
        normalized === "error"
    ) {
        return "status-failed";
    }

    return "status-processing";
}


// ---------------------------------------------------------
// Load individual document
// ---------------------------------------------------------

async function loadDocument(documentId) {

    try {

        const response =
            await fetch(
                `${API_BASE}/documents/${documentId}`
            );


        if (!response.ok) {
            throw new Error(
                "Unable to load document result."
            );
        }


        const document = await response.json();


        renderDocumentResult(document);


        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });


    } catch (error) {

        showError(
            error.message ||
            "Unable to load document result."
        );

        console.error(
            "Document result error:",
            error
        );
    }
}


// ---------------------------------------------------------
// Render document result
// ---------------------------------------------------------

function renderDocumentResult(document) {

    showElement(resultSection);


    resultDocumentName.textContent =
        document.document_name || "-";


    resultDocumentType.textContent =
        formatDocumentType(document.document_type);


    resultStatus.textContent =
        document.status || "-";


    resultCreatedAt.textContent =
        formatDate(document.created_at);


    renderExtractedData(
        document.extracted_data
    );


    renderValidationChecks(
        document.validation_checks
    );


    rawJson.textContent =
        JSON.stringify(
            document,
            null,
            2
        );
}


// ---------------------------------------------------------
// Render extracted data
// ---------------------------------------------------------

function renderExtractedData(data) {

    if (!data || Object.keys(data).length === 0) {

        extractedData.innerHTML = `
            <div class="empty-state">
                No extracted information available.
            </div>
        `;

        return;
    }


    extractedData.innerHTML =
        renderObject(data);
}


function renderObject(data) {

    if (
        data === null ||
        data === undefined
    ) {
        return `<span class="null-value">Not available</span>`;
    }


    if (
        typeof data !== "object"
    ) {
        return escapeHtml(data);
    }


    if (Array.isArray(data)) {

        if (data.length === 0) {
            return `<span class="null-value">No items</span>`;
        }

        return `
            <div class="array-container">
                ${data.map(item => `
                    <div class="array-item">
                        ${renderObject(item)}
                    </div>
                `).join("")}
            </div>
        `;
    }


    return `
        <div class="object-container">

            ${Object.entries(data).map(
                ([key, value]) => {

                    const isMissing =
                        value === null ||
                        value === undefined ||
                        value === "";


                    return `
                        <div class="field-row">

                            <div class="field-label">
                                ${escapeHtml(
                                    formatFieldName(key)
                                )}
                            </div>

                            <div class="field-value ${
                                isMissing
                                    ? "missing-field"
                                    : ""
                            }">

                                ${
                                    isMissing
                                        ? "Missing / Unreadable"
                                        : renderObject(value)
                                }

                            </div>

                        </div>
                    `;
                }
            ).join("")}

        </div>
    `;
}


function formatFieldName(key) {

    return key
        .replace(/_/g, " ")
        .replace(/\b\w/g, letter => letter.toUpperCase());
}


// ---------------------------------------------------------
// Render validation checks
// ---------------------------------------------------------

function renderValidationChecks(checks) {

    if (
        !checks ||
        checks.length === 0
    ) {

        validationData.innerHTML = `
            <div class="empty-state">
                No validation checks available.
            </div>
        `;

        return;
    }


    const table = document.createElement("table");

    table.className = "validation-table";


    table.innerHTML = `
        <thead>

            <tr>
                <th>Check</th>
                <th>Formula</th>
                <th>Calculated</th>
                <th>Reported</th>
                <th>Status</th>
            </tr>

        </thead>

        <tbody>

            ${checks.map(check => `

                <tr>

                    <td>
                        ${escapeHtml(check.check)}
                    </td>

                    <td>
                        ${escapeHtml(check.formula)}
                    </td>

                    <td>
                        ${formatValidationValue(
                            check.calculated_value
                        )}
                    </td>

                    <td>
                        ${formatValidationValue(
                            check.reported_value
                        )}
                    </td>

                    <td>
                        <span class="validation-status ${getValidationClass(check.status)}">
                            ${escapeHtml(check.status || "-")}
                        </span>
                    </td>

                </tr>

            `).join("")}

        </tbody>
    `;


    validationData.innerHTML = "";
    validationData.appendChild(table);
}


function formatValidationValue(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "—";
    }

    return escapeHtml(value);
}


function getValidationClass(status) {

    if (!status) {
        return "";
    }

    const normalized =
        status.toUpperCase();


    if (
        normalized === "PASS" ||
        normalized === "PASSED" ||
        normalized === "VALID"
    ) {
        return "validation-pass";
    }


    if (
        normalized === "FAIL" ||
        normalized === "FAILED" ||
        normalized === "INVALID"
    ) {
        return "validation-fail";
    }


    if (
        normalized === "NOT_APPLICABLE"
    ) {
        return "validation-na";
    }


    return "validation-na";
}


// ---------------------------------------------------------
// Close result
// ---------------------------------------------------------

closeResultButton.addEventListener(
    "click",
    () => {

        hideElement(resultSection);

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }
);


// ---------------------------------------------------------
// Copy JSON
// ---------------------------------------------------------

copyJsonButton.addEventListener(
    "click",
    async () => {

        try {

            await navigator.clipboard.writeText(
                rawJson.textContent
            );

            copyJsonButton.textContent =
                "Copied!";

            setTimeout(() => {
                copyJsonButton.textContent =
                    "Copy JSON";
            }, 1500);

        } catch (error) {

            console.error(
                "Copy failed:",
                error
            );

            showError(
                "Unable to copy JSON."
            );
        }
    }
);


// ---------------------------------------------------------
// Refresh dashboard
// ---------------------------------------------------------

refreshButton.addEventListener(
    "click",
    async () => {

        await loadDocuments();
    }
);


// ---------------------------------------------------------
// Initial page load
// ---------------------------------------------------------

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        await checkApiHealth();

        await loadDocuments();
    }
);