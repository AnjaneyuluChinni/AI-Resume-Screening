from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer, util
import os

model = SentenceTransformer('all-MiniLM-L6-v2')

def fuzzy_skill_match(resume_skills, jd_skills):
    matched = []
    missing = []
    for skill in jd_skills:
        found = False
        for rskill in resume_skills:
            if fuzz.token_set_ratio(skill.lower(), rskill.lower()) > 80:
                matched.append(skill)
                found = True
                break
        if not found:
            missing.append(skill)
    score = int(100 * len(matched) / max(1, len(jd_skills)))
    return score, matched, missing

def semantic_skill_match(resume_skills, jd_skills):
    resume_emb = model.encode(resume_skills, convert_to_tensor=True)
    jd_emb = model.encode(jd_skills, convert_to_tensor=True)
    sim_matrix = util.pytorch_cos_sim(jd_emb, resume_emb)
    matched = []
    missing = []
    for i, row in enumerate(sim_matrix):
        if row.max() > 0.7:
            matched.append(jd_skills[i])
        else:
            missing.append(jd_skills[i])
    score = int(100 * len(matched) / max(1, len(jd_skills)))
    return score, matched, missing 
