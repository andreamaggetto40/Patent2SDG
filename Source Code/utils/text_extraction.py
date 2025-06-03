"""
text_extraction.py

Provides functions to extract raw text from uploaded patent documents in PDF, TXT, and DOCX formats.
Also includes fallback logic using multiple libraries (PyMuPDF, PyPDF2) for robust PDF parsing.
"""

import fitz               # PyMuPDF
import docx               # python-docx
from PyPDF2 import PdfReader
import re

def extract_text_from_file(uploaded_file):
    """
    Extracts text from a single file-like object.

    Args:
        uploaded_file: A file object uploaded via Streamlit.

    Returns:
        str or None: Extracted text, or None if unsupported or unreadable.
    """
    if not uploaded_file:
        return None

    try:
        if uploaded_file.type == "application/pdf":
            # Primary PDF parsing using PyPDF2
            try:
                reader = PdfReader(uploaded_file)
                text = " ".join(page.extract_text() or "" for page in reader.pages)
                text = text.replace("\n", " ").strip()
                match = re.search(r"(?i)field of the invention.*", text)
                return ' '.join(text[match.start():match.start()+1000].split()) if match else ' '.join(text.split()[:300])
            except:
                # Fallback: use PyMuPDF
                with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                    return ' '.join(' '.join(p.get_text() for p in doc).split()[:300])
        elif uploaded_file.type == "text/plain":
            return uploaded_file.read().decode("utf-8", errors="ignore")
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return "\n".join(p.text for p in docx.Document(uploaded_file).paragraphs if p.text.strip())
    except:
        return None

    return None
