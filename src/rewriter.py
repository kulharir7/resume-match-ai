"""Rewriter Agent — rewrites resume sections optimized for the job description."""

from langchain_core.messages import HumanMessage, SystemMessage
from src.llm import get_llm


def rewrite_section(section_name: str, section_text: str, jd_text: str, missing_skills: list) -> str:
    """Rewrite a single resume section optimized for the JD."""
    llm = get_llm()
    
    missing_str = ", ".join(missing_skills) if missing_skills else "none"
    
    prompt = f"""You are an expert resume writer and ATS optimizer. Rewrite this resume section to better match the job description.

SECTION: {section_name.upper()}
ORIGINAL TEXT:
{section_text}

JOB DESCRIPTION (key parts):
{jd_text[:2000]}

MISSING SKILLS TO INCORPORATE (if relevant): {missing_str}

RULES:
1. Keep all REAL information — do NOT fabricate experience or skills
2. Add missing keywords NATURALLY where truthful
3. Use strong action verbs (Led, Developed, Implemented, Achieved)
4. Quantify achievements where possible (%, $, numbers)
5. Keep it concise — ATS prefers clear, scannable text
6. Match the tone and terminology of the job description
7. Do NOT add skills the person clearly doesn't have

Output ONLY the rewritten section text. No explanations."""

    response = llm.invoke([
        SystemMessage(content="You are a professional resume writer. Rewrite sections to be ATS-optimized while keeping all information truthful."),
        HumanMessage(content=prompt)
    ])
    return response.content.strip()


def rewrite_full_resume(resume_sections: dict, jd_text: str, missing_skills: list) -> dict:
    """Rewrite all resume sections."""
    rewritten = {}
    
    sections_to_rewrite = ["summary", "experience", "skills", "projects"]
    
    for section_name, section_text in resume_sections.items():
        if section_name in sections_to_rewrite and section_text.strip():
            rewritten[section_name] = rewrite_section(
                section_name, section_text, jd_text, missing_skills
            )
        else:
            rewritten[section_name] = section_text
    
    return rewritten


def generate_summary(resume_text: str, jd_text: str) -> str:
    """Generate a tailored professional summary."""
    llm = get_llm()
    
    prompt = f"""Write a professional summary (3-4 sentences) for this person's resume, tailored to this job.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{jd_text[:1500]}

RULES:
- 3-4 sentences max
- Include relevant keywords from the JD
- Highlight most relevant experience
- Use strong, professional language
- Be truthful — only mention skills/experience that exist in the resume

Output ONLY the summary. No explanations."""

    response = llm.invoke([
        SystemMessage(content="You write concise, ATS-optimized professional summaries."),
        HumanMessage(content=prompt)
    ])
    return response.content.strip()
