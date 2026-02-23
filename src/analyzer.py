"""Analyzer Agent — calculates match score between resume and job description."""

import re
from langchain_core.messages import HumanMessage, SystemMessage
from src.llm import get_llm
from src.parser import extract_sections, extract_keywords_from_jd, extract_contact_info


def calculate_keyword_match(resume_text: str, jd_keywords: dict) -> dict:
    """Calculate keyword match between resume and JD."""
    resume_lower = resume_text.lower()
    
    # Hard skills match
    found_hard = []
    missing_hard = []
    for skill in jd_keywords["hard_skills"]:
        if re.search(r'\b' + re.escape(skill) + r'\b', resume_lower):
            found_hard.append(skill)
        else:
            missing_hard.append(skill)
    
    hard_score = (len(found_hard) / max(len(jd_keywords["hard_skills"]), 1)) * 100
    
    # Soft skills match
    found_soft = []
    missing_soft = []
    for skill in jd_keywords["soft_skills"]:
        if skill in resume_lower:
            found_soft.append(skill)
        else:
            missing_soft.append(skill)
    
    soft_score = (len(found_soft) / max(len(jd_keywords["soft_skills"]), 1)) * 100
    
    return {
        "hard_skills": {"found": found_hard, "missing": missing_hard, "score": round(hard_score)},
        "soft_skills": {"found": found_soft, "missing": missing_soft, "score": round(soft_score)},
    }


def check_ats_formatting(resume_text: str, filename: str) -> dict:
    """Check ATS compatibility of resume formatting."""
    issues = []
    score = 100
    
    # Check file type
    if filename.lower().endswith('.pdf'):
        file_type_ok = True
    elif filename.lower().endswith('.docx'):
        file_type_ok = True
    else:
        file_type_ok = False
        issues.append("Use PDF or DOCX format for best ATS compatibility")
        score -= 15
    
    # Check length
    word_count = len(resume_text.split())
    if word_count < 150:
        issues.append(f"Resume too short ({word_count} words). Aim for 400-800 words.")
        score -= 20
    elif word_count > 1200:
        issues.append(f"Resume too long ({word_count} words). Keep it under 800 words for 1 page.")
        score -= 10
    
    # Check for contact info
    contact = extract_contact_info(resume_text)
    if not contact["email"]:
        issues.append("No email found — ATS needs this")
        score -= 15
    if not contact["phone"]:
        issues.append("No phone number found")
        score -= 10
    
    # Check for common sections
    sections = extract_sections(resume_text)
    required = ["experience", "education", "skills"]
    for sec in required:
        if sec not in sections:
            issues.append(f"Missing '{sec.title()}' section — most ATS look for this")
            score -= 10
    
    # Check for action verbs
    action_verbs = ["managed", "developed", "led", "created", "implemented", "designed",
                    "built", "improved", "reduced", "increased", "achieved", "delivered"]
    found_verbs = [v for v in action_verbs if v in resume_text.lower()]
    if len(found_verbs) < 3:
        issues.append("Add more action verbs (managed, developed, led, improved...)")
        score -= 10
    
    # Check for quantified achievements
    has_numbers = bool(re.findall(r'\d+%|\$\d+|\d+\+', resume_text))
    if not has_numbers:
        issues.append("Add quantified achievements (e.g., 'improved performance by 35%')")
        score -= 10
    
    return {
        "score": max(score, 0),
        "file_type_ok": file_type_ok,
        "word_count": word_count,
        "contact": contact,
        "sections_found": list(sections.keys()),
        "action_verbs_found": found_verbs,
        "has_metrics": has_numbers,
        "issues": issues,
    }


def analyze_with_llm(resume_text: str, jd_text: str) -> dict:
    """Use LLM for deep analysis — experience relevance, suggestions."""
    llm = get_llm()
    
    prompt = f"""You are an expert ATS resume analyzer. Analyze this resume against the job description.

JOB DESCRIPTION:
{jd_text[:3000]}

RESUME:
{resume_text[:3000]}

Provide a JSON response with EXACTLY this structure (no markdown, just raw JSON):
{{
    "experience_relevance_score": <0-100>,
    "experience_analysis": "<brief analysis>",
    "education_score": <0-100>,
    "education_analysis": "<brief analysis>",
    "overall_fit": "<1-2 sentence summary>",
    "top_suggestions": [
        "<suggestion 1>",
        "<suggestion 2>",
        "<suggestion 3>",
        "<suggestion 4>",
        "<suggestion 5>"
    ],
    "strengths": [
        "<strength 1>",
        "<strength 2>",
        "<strength 3>"
    ],
    "weaknesses": [
        "<weakness 1>",
        "<weakness 2>",
        "<weakness 3>"
    ]
}}

Output ONLY valid JSON. No explanation, no markdown."""

    response = llm.invoke([
        SystemMessage(content="You are an ATS resume expert. Output ONLY valid JSON."),
        HumanMessage(content=prompt)
    ])
    
    # Parse JSON from response
    import json
    try:
        # Try to extract JSON from response
        text = response.content.strip()
        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text.strip())
        return result
    except (json.JSONDecodeError, IndexError):
        return {
            "experience_relevance_score": 50,
            "experience_analysis": "Could not analyze — try again",
            "education_score": 50,
            "education_analysis": "Could not analyze",
            "overall_fit": response.content[:200],
            "top_suggestions": ["Ensure resume matches job keywords"],
            "strengths": ["Resume submitted for analysis"],
            "weaknesses": ["Analysis incomplete — try again"],
        }


def full_analysis(resume_text: str, jd_text: str, filename: str) -> dict:
    """Run complete analysis: keywords + ATS + LLM deep analysis."""
    # 1. Extract JD keywords
    jd_keywords = extract_keywords_from_jd(jd_text)
    
    # 2. Keyword matching
    keyword_match = calculate_keyword_match(resume_text, jd_keywords)
    
    # 3. ATS formatting check
    ats_check = check_ats_formatting(resume_text, filename)
    
    # 4. LLM deep analysis
    llm_analysis = analyze_with_llm(resume_text, jd_text)
    
    # 5. Calculate overall score
    hard_score = keyword_match["hard_skills"]["score"]
    exp_score = llm_analysis.get("experience_relevance_score", 50)
    edu_score = llm_analysis.get("education_score", 50)
    ats_score = ats_check["score"]
    
    # Weighted average
    overall = round(
        hard_score * 0.35 +
        exp_score * 0.30 +
        edu_score * 0.10 +
        ats_score * 0.15 +
        keyword_match["soft_skills"]["score"] * 0.10
    )
    
    return {
        "overall_score": overall,
        "hard_skills": keyword_match["hard_skills"],
        "soft_skills": keyword_match["soft_skills"],
        "experience": {
            "score": exp_score,
            "analysis": llm_analysis.get("experience_analysis", ""),
        },
        "education": {
            "score": edu_score,
            "analysis": llm_analysis.get("education_analysis", ""),
        },
        "ats": ats_check,
        "overall_fit": llm_analysis.get("overall_fit", ""),
        "suggestions": llm_analysis.get("top_suggestions", []),
        "strengths": llm_analysis.get("strengths", []),
        "weaknesses": llm_analysis.get("weaknesses", []),
        "jd_keywords": jd_keywords,
        "contact": ats_check["contact"],
    }
