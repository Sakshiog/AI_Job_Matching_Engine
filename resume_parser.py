from pathlib import Path
from pypdf import PdfReader
from docx import Document


def extract_pdf_text(file_path):
    reader = PdfReader(str(file_path))

    text = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text).strip()


def extract_docx_text(file_path):
    document = Document(str(file_path))

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text.strip())

    return "\n".join(text).strip()


def extract_resume_text(file_path):
    file_path = Path(file_path)

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension == ".docx":
        return extract_docx_text(file_path)

    else:
        raise ValueError("Only PDF and DOCX resumes are supported.")