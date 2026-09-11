from pathlib import Path

import pymupdf


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}

MAX_PAGES = 3


def validate_file(file_path: str) -> dict:
    """
    Validate file type, size/content, integrity, and page count.
    """

    path = Path(file_path)

    # Check that the file exists
    if not path.exists():
        return {
            "valid": False,
            "error": "File does not exist.",
        }

    # Check file extension
    extension = path.suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return {
            "valid": False,
            "error": f"Unsupported file type: {extension}",
        }

    # Check that the file is not empty
    if path.stat().st_size == 0:
        return {
            "valid": False,
            "error": "File is empty.",
        }

    # PDF-specific validation
    if extension == ".pdf":
        try:
            pdf = pymupdf.open(file_path)

            page_count = len(pdf)

            if page_count == 0:
                pdf.close()
                return {
                    "valid": False,
                    "error": "PDF contains no pages.",
                }

            if page_count > MAX_PAGES:
                pdf.close()
                return {
                    "valid": False,
                    "error": (
                        f"PDF contains {page_count} pages. "
                        f"Maximum allowed is {MAX_PAGES}."
                    ),
                }

            pdf.close()

            return {
                "valid": True,
                "file_type": extension,
                "page_count": page_count,
            }

        except Exception:
            return {
                "valid": False,
                "error": "PDF is corrupted or cannot be opened.",
            }

    # Image validation
    try:
        from PIL import Image

        image = Image.open(file_path)
        image.verify()

        return {
            "valid": True,
            "file_type": extension,
            "page_count": 1,
        }

    except Exception:
        return {
            "valid": False,
            "error": "Image is corrupted or cannot be opened.",
        }