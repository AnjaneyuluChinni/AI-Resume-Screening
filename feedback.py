import os

# --- Google Service Account Credentials for Streamlit Cloud ---
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
    with open("/tmp/gcp-sa.json", "w") as f:
        f.write(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/gcp-sa.json"

from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI

load_dotenv()

def generate_feedback(candidate, job_description, missing_skills):
    prompt = f"""
You are an expert career coach. Given the following candidate details and job description, provide:
- A brief summary of the candidate's fit
- Suggestions for improving the resume to better match the job
- How to address missing skills: {', '.join(missing_skills)}

Candidate Details:
Name: {candidate.get('name', '')}
Email: {candidate.get('email', '')}
Skills: {candidate.get('skills', '')}
Education: {candidate.get('education', '')}
Experience: {candidate.get('experience', '')}

Job Description:
{job_description}
"""
    llm = ChatVertexAI(model="gemini-1.5-pro-preview-0409", project=os.getenv("GCP_PROJECT"), location=os.getenv("GCP_LOCATION", "us-central1"))
    return llm.invoke(prompt)
