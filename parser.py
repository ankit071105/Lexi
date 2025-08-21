import io
import pdfplumber
from docx import Document

def extract_text(filename, content):
    if filename.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return content.decode()  # fallback for .txt, .eml etc.
