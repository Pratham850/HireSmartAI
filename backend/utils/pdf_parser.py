import logging

logger = logging.getLogger("hiresmart.pdf_parser")


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw plain text from a PDF resume file using PyMuPDF (fitz) with PyPDF2 fallback."""
    text_content = []
    
    # Try PyMuPDF (fitz)
    try:
        import fitz
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content.append(page.get_text("text"))
        doc.close()
        full_text = "\n".join(text_content).strip()
        if full_text:
            logger.info(f"PyMuPDF successfully extracted {len(full_text)} chars from {pdf_path}")
            return full_text
    except ImportError:
        logger.warning("PyMuPDF (fitz) not installed. Trying fallback PDF extractors...")
    except Exception as exc:
        logger.error(f"PyMuPDF error reading {pdf_path}: {exc}")

    # Fallback to PyPDF2 or pypdf if fitz is missing
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        for page in reader.pages:
            text_content.append(page.extract_text() or "")
        full_text = "\n".join(text_content).strip()
        if full_text:
            return full_text
    except Exception:
        pass

    # Final text extraction fallback
    try:
        with open(pdf_path, "r", errors="ignore") as f:
            return f.read()
    except Exception as exc:
        logger.error(f"All PDF text extraction attempts failed for {pdf_path}: {exc}")
        return ""
