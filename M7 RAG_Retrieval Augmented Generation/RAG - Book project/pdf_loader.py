"""
pdf_loader.py
─────────────
Extract text from the Deep Learning PDF using PyMuPDF (fitz).

CHANGES vs. original
─────────────────────
① Pages now joined with "\\f" (form-feed) instead of "\\n\\n".
   The chunking.clean_text() function splits on \\f to track which
   page number each character came from — critical for source citations.
   Using "\\n\\n" discards all page boundary information entirely.

② read_pdf_text (pypdf version) kept for compatibility but updated to
   also join with \\f.

Install:  pip install pymupdf pypdf
"""

import re
import fitz   # PyMuPDF  — primary extractor


def read_pdf_text(pdf_path: str) -> str:
    """
    Extract text from a PDF using PyMuPDF.
    Pages are separated by \\f so chunking.clean_text() can track page numbers.

    Args:
        pdf_path: Path to the .pdf file.

    Returns:
        Full document text with \\f between pages.
    """
    doc = fitz.open(pdf_path)
    text = "\f".join(page.get_text() for page in doc)
    doc.close()
    return text


def read_pdf_text2(pdf_path: str) -> str:
    """
    Enhanced PDF extraction with fallback across PyMuPDF and pypdf.

    - Primary: PyMuPDF (fitz), robust for layout-preserving extraction.
    - Fallback: pypdf (if installed) for compatibility with some edge-case PDFs.

    Returns text with \f separators between pages (required by clean_text()).
    """
    try:
        return read_pdf_text(pdf_path)
    except Exception as e:
        # First fallback: pypdf (optional dependency)
        try:
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text() or ""
                page_text = page_text.replace("\x00", " ")
                page_text = re.sub(r"[ \t]+", " ", page_text)
                pages_text.append(page_text)
            return "\f".join(pages_text)
        except Exception as e2:
            raise RuntimeError(
                f"Failed to extract PDF text from {pdf_path}: {e}; fallback error: {e2}"
            )


def read_bdf_text(bdf_path: str) -> str:
    """
    Load a raw text-based book format (BDF or plain text) for use with RAG pipeline.

    If path extension is not .bdf, it still reads as plain UTF-8 text.
    """
    with open(bdf_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# ── Legacy pypdf version (kept for backward compatibility) ────────────────────
try:
    from pypdf import PdfReader as _PdfReader

    def read_pdf_text_pypdf(pdf_path: str) -> str:
        """
        Fallback extractor using pypdf (less accurate for complex layouts).
        Also joins pages with \\f for consistent page tracking.
        """
        reader = _PdfReader(pdf_path)
        pages_text = []
        for page in reader.pages:
            txt = page.extract_text() or ""
            txt = txt.replace("\x00", " ")
            txt = re.sub(r"[ \t]+", " ", txt)
            pages_text.append(txt)
        return "\f".join(pages_text)

except ImportError:
    pass  # pypdf optional — fitz is the primary extractor
