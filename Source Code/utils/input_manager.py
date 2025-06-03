"""
input_manager.py

Provides utilities to extract text content from uploaded patent files:
- PDF
- XML (especially EPO XML)
- Mixed ZIP archives (including nested ZIPs)

Used in the main Streamlit app for parsing and processing user input.
"""

import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from utils.text_extraction import extract_text_from_file

def extract_texts_from_pdf_batch(uploaded_files, st_ref=None):
    """
    Extracts text from a list of uploaded PDF files.

    Args:
        uploaded_files (List): List of uploaded PDF files.
        st_ref (streamlit): Optional Streamlit reference to display warnings/errors.

    Returns:
        dict: filename -> extracted text.
    """
    texts = {}
    for file in uploaded_files:
        try:
            extracted = extract_text_from_file(file)
            if extracted:
                texts[file.name] = extracted.strip()
            elif st_ref:
                st_ref.warning(f"Could not extract valid text from: {file.name}")
        except Exception as e:
            if st_ref:
                st_ref.error(f"Error reading {file.name}: {e}")
    return texts

def extract_text_from_ep_xml_file(uploaded_file, max_chars=5000):
    """
    Extracts and truncates text from an EPO XML patent file.

    Args:
        uploaded_file: XML file uploaded by user.
        max_chars (int): Max number of characters to return.

    Returns:
        dict: filename -> text or empty dict if invalid.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp:
            tmp.write(uploaded_file.read())
            text = extract_text_from_ep_xml(tmp.name, max_chars)
        return {uploaded_file.name: text} if text else {}
    except Exception:
        return {}
    finally:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)

def extract_text_from_ep_xml(xml_path, max_chars=5000):
    """
    Parses XML and extracts <abstract>, <description>, and <claims> sections.

    Args:
        xml_path (str): Path to the local XML file.
        max_chars (int): Character limit.

    Returns:
        str or None: Extracted content.
    """
    try:
        root = ET.parse(xml_path).getroot()
        def extract(tag):
            s = root.find(f".//{tag}")
            return " ".join(e.text for e in s.iter() if e.text) if s is not None else ""
        content = " ".join([extract(t) for t in ["abstract", "description", "claims"]]).strip()
        return content[:max_chars] if content else None
    except Exception:
        return None

def extract_texts_from_zip_any_structure(zip_path, st_ref=None, max_chars=5000):
    """
    Extracts texts from a ZIP archive with arbitrary nesting and structure.

    Args:
        zip_path (str): Path to the outer ZIP file.
        st_ref: Optional Streamlit UI reference.
        max_chars (int): Truncate long text.

    Returns:
        dict: filename -> extracted text from PDFs, XMLs, TXT, DOCX.
    """
    results = {}

    def process_directory(directory):
        for root, _, files in os.walk(directory):
            for f in files:
                path = os.path.join(root, f)

                if f.endswith(".zip"):
                    # Recursively process nested ZIPs
                    with tempfile.TemporaryDirectory() as inner_dir:
                        try:
                            with zipfile.ZipFile(path, 'r') as z:
                                z.extractall(inner_dir)
                            process_directory(inner_dir)
                        except Exception as e:
                            if st_ref:
                                st_ref.warning(f"Failed to extract nested zip {f}: {e}")
                elif f.endswith(".xml") and f.lower() != "toc.xml":
                    try:
                        text = extract_text_from_ep_xml(path, max_chars)
                        if text:
                            results[f] = text
                    except Exception as e:
                        if st_ref:
                            st_ref.warning(f"Failed parsing XML {f}: {e}")
                elif f.endswith(".pdf") or f.endswith(".docx") or f.endswith(".txt"):
                    try:
                        with open(path, "rb") as fobj:
                            text = extract_text_from_file(fobj)
                            if text:
                                results[f] = text.strip()
                    except Exception as e:
                        if st_ref:
                            st_ref.warning(f"Failed to parse {f}: {e}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmp_dir)
            process_directory(tmp_dir)
        except Exception as e:
            if st_ref:
                st_ref.error(f"Could not process ZIP: {e}")

    return results
