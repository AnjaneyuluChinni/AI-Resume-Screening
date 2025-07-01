import pdfplumber
import docx
import re
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = " ".join(page.extract_text() or '' for page in pdf.pages)
        return text
    except Exception:
        # fallback to unstructured
        elements = partition_pdf(file)
        return " ".join([el.text for el in elements if hasattr(el, 'text')])

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = " ".join([para.text for para in doc.paragraphs])
        return text
    except Exception:
        # fallback to unstructured
        elements = partition_docx(file)
        return " ".join([el.text for el in elements if hasattr(el, 'text')])

def extract_email(text):
    match = re.search(EMAIL_REGEX, text)
    return match.group(0) if match else None

def extract_name(text):
    # Heuristic: first line or first capitalized phrase
    lines = text.splitlines()
    for line in lines:
        if line.strip() and len(line.split()) <= 4:
            return line.strip()
    return None

def parse_resume(file, filetype):
    if filetype == 'pdf':
        text = extract_text_from_pdf(file)
    elif filetype == 'docx':
        text = extract_text_from_docx(file)
    else:
        raise ValueError('Unsupported file type')
    email = extract_email(text)
    name = extract_name(text)
    # Skills, Education, Experience will be extracted by LLM
    return {
        'raw_text': text,
        'name': name,
        'email': email
    } 