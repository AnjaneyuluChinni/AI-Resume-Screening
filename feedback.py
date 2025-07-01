import os
from dotenv import load_dotenv
from google.cloud import aiplatform

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
    # Set your project and location
    project = os.getenv("GCP_PROJECT")
    location = os.getenv("GCP_LOCATION", "us-central1")
    model = "gemini-1.5-pro-preview-0409"  # or the latest available

    aiplatform.init(project=project, location=location)
    endpoint = aiplatform.Endpoint(
        endpoint_name=f"projects/{project}/locations/{location}/publishers/google/models/{model}"
    )
    response = endpoint.predict(instances=[{"content": prompt}])
    return response.predictions[0]['content']
