import os
from transformers import pipeline

def get_hf_pipeline():
    # You can change the model to any supported chat/completion model
    model_id = "HuggingFaceH4/zephyr-7b-beta"
    hf_token = os.getenv("HF_TOKEN")
    return pipeline("text-generation", model=model_id, token=hf_token)

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
    pipe = get_hf_pipeline()
    result = pipe(prompt, max_new_tokens=512, do_sample=True)
    return result[0]['generated_text']
