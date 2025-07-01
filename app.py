import os
import streamlit as st
import tempfile
from resume_parser import parse_resume
from scorer import fuzzy_skill_match, semantic_skill_match
from feedback import generate_feedback, get_hf_pipeline
from dotenv import load_dotenv
import json
import re

load_dotenv()
st.set_page_config(page_title="martResumeScan - AI Resume Screening", layout="centered")
st.title("martResumeScan :mag_right:")
st.write("AI-powered resume screening and feedback tool.")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
jd = st.text_area("Paste Job Description", height=200)

def extract_resume_info(raw_text):
    prompt = f'''Extract the following from the resume text below. Return as JSON with keys: skills (list), education (string), experience (string).\nResume Text:\n{raw_text}\n'''
    pipe = get_hf_pipeline()
    result = pipe(prompt, max_new_tokens=512, do_sample=True)
    try:
        json_str = re.search(r'\{.*\}', result[0]['generated_text'], re.DOTALL).group(0)
        return json.loads(json_str)
    except Exception:
        return {'skills': [], 'education': '', 'experience': ''}

def extract_jd_skills(jd):
    prompt = f'''Extract a list of required skills from the following job description. Return as a Python list.\nJob Description:\n{jd}\n'''
    pipe = get_hf_pipeline()
    result = pipe(prompt, max_new_tokens=256, do_sample=True)
    try:
        list_str = re.search(r'\[.*\]', result[0]['generated_text'], re.DOTALL).group(0)
        return json.loads(list_str)
    except Exception:
        return []

if uploaded_file and jd:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    filetype = uploaded_file.name.split('.')[-1].lower()
    parsed = parse_resume(tmp_path, filetype)
    st.subheader("Extracted Candidate Details")
    st.write(f"**Name:** {parsed.get('name', 'N/A')}")
    st.write(f"**Email:** {parsed.get('email', 'N/A')}")
    # Use Hugging Face LLM to extract skills, education, experience
    extracted = extract_resume_info(parsed['raw_text'])
    st.write(f"**Skills:** {', '.join(extracted.get('skills', []))}")
    st.write(f"**Education:** {extracted.get('education', '')}")
    st.write(f"**Experience:** {extracted.get('experience', '')}")
    # Skill matching
    jd_skills = [s.strip() for s in st.text_input("Comma-separated required skills (optional, for better matching)").split(',') if s.strip()]
    if not jd_skills:
        jd_skills = extract_jd_skills(jd)
    st.write(f"**Job Skills:** {', '.join(jd_skills)}")
    # Scoring
    score, matched, missing = fuzzy_skill_match(extracted.get('skills', []), jd_skills)
    st.subheader(f"Match Score: {score}/100")
    st.progress(score)
    st.write(f"**Matched Skills:** {', '.join(matched)}")
    st.write(f"**Missing Skills:** {', '.join(missing)}")
    # Feedback
    feedback = generate_feedback({
        'name': parsed.get('name'),
        'email': parsed.get('email'),
        'skills': extracted.get('skills', []),
        'education': extracted.get('education', ''),
        'experience': extracted.get('experience', '')
    }, jd, missing)
    st.subheader("Improvement Suggestions")
    st.write(feedback)
    os.remove(tmp_path)
else:
    st.info("Please upload a resume and paste a job description to begin.") 
