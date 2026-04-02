from pypdf import PdfReader
import os
import re


def clean_text(text: str) -> str:
    """
    Cleans extracted PDF text by removing noise like headers,
    footers, URLs, and unnecessary whitespace.
    """

    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        #  Skip empty lines
        if not line:
            continue

        # Remove URLs (generic)
        if "http" in line or "www" in line:
            continue

        #  Remove page numbers (e.g., "Page 1", "1", etc.)
        if re.match(r"^page\s*\d+", line.lower()):
            continue
        if re.match(r"^\d+$", line):
            continue

        #  Remove excessive symbols / navigation marks
        if "▸" in line or "◂" in line:
            continue

        # Fix broken words like "fromtyping" → "from typing"
        line = re.sub(r"([a-z])([A-Z])", r"\1 \2", line)

        cleaned_lines.append(line)

    # Join back into cleaned text
    cleaned_text = "\n".join(cleaned_lines)

    # Normalize multiple spaces
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)

    return cleaned_text.strip()


def load_pdfs_from_directory(directory_path, source_name, domain):
    documents = []

    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory_path, filename)
            reader = PdfReader(file_path)

            fname = filename.lower()
            doc_type = "unknown"

            if "leave" in fname:
                doc_type = "leave_policy"
            elif "contract" in fname:
                doc_type = "employment_contract"
            elif "communication" in fname:
                doc_type = "communication"

            for page_number, page in enumerate(reader.pages):
                text = page.extract_text()

                if text and isinstance(text, str):
                    text = clean_text(text)

                    if not text.strip() or len(text) < 50:
                        continue

                    documents.append({
                        "text": text,
                        "metadata": {
                            "source": source_name,
                            "domain": domain,
                            "doc_type": doc_type,
                            "file_name": filename,
                            "page": page_number + 1,
                        },
                    })

    return documents