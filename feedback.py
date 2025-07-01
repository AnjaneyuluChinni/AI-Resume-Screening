import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def generate_feedback(candidate, job_description, missing_skills):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
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
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are an expert career coach."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content 
