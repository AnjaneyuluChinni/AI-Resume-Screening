import streamlit as st
import tempfile
import os
from resume_parser import parse_resume
from scorer import fuzzy_skill_match, semantic_skill_match
from feedback import generate_feedback
from dotenv import load_dotenv
from google.cloud import aiplatform
import json

load_dotenv()
st.set_page_config(page_title="martResumeScan - AI Resume Screening", layout="centered")
st.title("martResumeScan :mag_right:")
st.write("AI-powered resume screening and feedback tool.")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
jd = st.text_area("Paste Job Description", height=200)

# Google Cloud Vertex AI setup
gcp_project = os.getenv("GCP_PROJECT")
gcp_location = os.getenv("GCP_LOCATION", "us-central1")
model = "gemini-1.5-pro-preview-0409"  # or latest available
aiplatform.init(project=gcp_project, location=gcp_location)
endpoint = aiplatform.Endpoint(
    endpoint_name=f"projects/{gcp_project}/locations/{gcp_location}/publishers/google/models/{model}"
)

def gemini_completion(prompt):
    response = endpoint.predict(instances=[{"content": prompt}])
    # The response format may vary; adjust as needed
    try:
        return response.predictions[0]["content"]
    except Exception:
        return "[Error: Could not parse Gemini response]"

if uploaded_file and jd:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    filetype = uploaded_file.name.split('.')[-1].lower()
    parsed = parse_resume(tmp_path, filetype)
    st.subheader("Extracted Candidate Details")
    st.write(f"**Name:** {parsed.get('name', 'N/A')}")
    st.write(f"**Email:** {parsed.get('email', 'N/A')}")
    # Use Gemini to extract skills, education, experience
    extraction_prompt = f'''Extract the following from the resume text below. Return as JSON with keys: skills (list), education (string), experience (string).\nResume Text:\n{parsed['raw_text']}\n'''
    extraction_content = gemini_completion(extraction_prompt)
    try:
        extracted = json.loads(extraction_content)
    except Exception:
        extracted = {'skills': [], 'education': '', 'experience': ''}
    st.write(f"**Skills:** {', '.join(extracted.get('skills', []))}")
    st.write(f"**Education:** {extracted.get('education', '')}")
    st.write(f"**Experience:** {extracted.get('experience', '')}")
    # Skill matching
    jd_skills = [s.strip() for s in st.text_input("Comma-separated required skills (optional, for better matching)").split(',') if s.strip()]
    if not jd_skills:
        # Try to extract skills from JD using Gemini
        skill_prompt = f'''Extract a list of required skills from the following job description. Return as a Python list.\nJob Description:\n{jd}\n'''
        skill_content = gemini_completion(skill_prompt)
        try:
            jd_skills = json.loads(skill_content)
        except Exception:
            jd_skills = []
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
    }, jd, missing, gemini_completion)
    st.subheader("Improvement Suggestions")
    st.write(feedback)
    os.remove(tmp_path)
else:
    st.info("Please upload a resume and paste a job description to begin.") 
