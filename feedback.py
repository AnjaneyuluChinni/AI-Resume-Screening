from langchain_community.chat_models import ChatGroq
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()
llm = ChatGroq(groq_api_key=os.getenv('GROQ_API_KEY'), model="mixtral-8x7b-32768")

SUGGESTION_PROMPT = """
You are an expert career coach. Given the following candidate details and job description, provide:
- A brief summary of the candidate's fit
- Suggestions for improving the resume to better match the job
- How to address missing skills: {missing_skills}

Candidate Details:
Name: {name}
Email: {email}
Skills: {skills}
Education: {education}
Experience: {experience}

Job Description:
{job_description}
"""

def generate_feedback(candidate, job_description, missing_skills):
    prompt = ChatPromptTemplate.from_template(SUGGESTION_PROMPT)
    chain = prompt | llm
    result = chain.invoke({
        'name': candidate.get('name', ''),
        'email': candidate.get('email', ''),
        'skills': candidate.get('skills', ''),
        'education': candidate.get('education', ''),
        'experience': candidate.get('experience', ''),
        'job_description': job_description,
        'missing_skills': ', '.join(missing_skills)
    })
    return result.content 
