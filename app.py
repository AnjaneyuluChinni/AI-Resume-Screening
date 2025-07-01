import streamlit as st
import tempfile
import os
from resume_parser import parse_resume
from scorer import fuzzy_skill_match, semantic_skill_match
from feedback import generate_feedback
from langchain_community.chat_models import ChatGroq
from langchain.prompts import ChatPromptTemplate    
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="martResumeScan - AI Resume Screening", layout="centered")
st.title("martResumeScan :mag_right:")
st.write("AI-powered resume screening and feedback tool.")

uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
jd = st.text_area("Paste Job Description", height=200)

groq_api_key = os.getenv('GROQ_API_KEY')
llm = ChatGroq(groq_api_key=groq_api_key, model="mixtral-8x7b-32768")

if uploaded_file and jd:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name
    filetype = uploaded_file.name.split('.')[-1].lower()
    parsed = parse_resume(tmp_path, filetype)
    st.subheader("Extracted Candidate Details")
    st.write(f"**Name:** {parsed.get('name', 'N/A')}")
    st.write(f"**Email:** {parsed.get('email', 'N/A')}")
    # Use LLM to extract skills, education, experience
    extraction_prompt = ChatPromptTemplate.from_template('''Extract the following from the resume text below. Return as JSON with keys: skills (list), education (string), experience (string).\nResume Text:\n{resume_text}\n''')
    chain = extraction_prompt | llm
    extraction = chain.invoke({'resume_text': parsed['raw_text']})
    import json
    try:
        extracted = json.loads(extraction.content)
    except Exception:
        extracted = {'skills': [], 'education': '', 'experience': ''}
    st.write(f"**Skills:** {', '.join(extracted.get('skills', []))}")
    st.write(f"**Education:** {extracted.get('education', '')}")
    st.write(f"**Experience:** {extracted.get('experience', '')}")
    # Skill matching
    jd_skills = [s.strip() for s in st.text_input("Comma-separated required skills (optional, for better matching)").split(',') if s.strip()]
    if not jd_skills:
        # Try to extract skills from JD using LLM
        skill_prompt = ChatPromptTemplate.from_template('''Extract a list of required skills from the following job description. Return as a Python list.\nJob Description:\n{jd}\n''')
        skill_chain = skill_prompt | llm
        skill_extraction = skill_chain.invoke({'jd': jd})
        try:
            jd_skills = json.loads(skill_extraction.content)
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
    }, jd, missing)
    st.subheader("Improvement Suggestions")
    st.write(feedback)
    os.remove(tmp_path)
else:
    st.info("Please upload a resume and paste a job description to begin.") 
