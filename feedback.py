import os
import google.generativeai as genai

def generate_feedback(candidate, job_description, missing_skills):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
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
    response = model.generate_content(prompt)
    return response.text
