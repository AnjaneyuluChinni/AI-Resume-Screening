from fuzzywuzzy import fuzz

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
