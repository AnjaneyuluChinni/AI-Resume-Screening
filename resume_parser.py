import pdfplumber
import docx
import re

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = " ".join(page.extract_text() or '' for page in pdf.pages)
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = " ".join([para.text for para in doc.paragraphs])
    return text

def extract_email(text):
    match = re.search(EMAIL_REGEX, text)
    return match.group(0) if match else None

def extract_name(text):
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
    return {
        'raw_text': text,
        'name': name,
        'email': email
    }
