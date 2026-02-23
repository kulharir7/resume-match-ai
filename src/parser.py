"""Resume & JD parser — extracts text, sections, and structured data."""

import re
import os
import tempfile
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        reader = PdfReader(tmp_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    finally:
        os.unlink(tmp_path)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes."""
    from docx import Document
    import io
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


def extract_resume_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from resume file (PDF or DOCX)."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(file_bytes)
    elif ext in (".txt", ".md"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def extract_contact_info(text: str) -> dict:
    """Extract email, phone, name from resume text."""
    email = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    phone = re.findall(r'[\+]?[\d\s\-\(\)]{10,15}', text)
    
    # Name is usually the first non-empty line
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    name = lines[0] if lines else "Unknown"
    # Clean name — remove if it looks like email/phone
    if '@' in name or re.match(r'^[\d\+\-\(\)\s]+$', name):
        name = lines[1] if len(lines) > 1 else "Unknown"
    
    return {
        "name": name,
        "email": email[0] if email else None,
        "phone": phone[0].strip() if phone else None,
    }


def extract_sections(text: str) -> dict:
    """Split resume into sections (experience, education, skills, etc.)."""
    section_headers = {
        "summary": r"(?i)(summary|objective|profile|about\s*me)",
        "experience": r"(?i)(experience|work\s*history|employment|professional\s*experience)",
        "education": r"(?i)(education|academic|qualification|degree)",
        "skills": r"(?i)(skills|technical\s*skills|technologies|competenc)",
        "projects": r"(?i)(projects|portfolio|personal\s*projects)",
        "certifications": r"(?i)(certification|certificate|license|credential)",
    }
    
    sections = {}
    lines = text.split('\n')
    current_section = "header"
    current_lines = []
    
    for line in lines:
        matched = False
        for section_name, pattern in section_headers.items():
            if re.search(pattern, line) and len(line.strip()) < 60:
                # Save previous section
                if current_lines:
                    sections[current_section] = '\n'.join(current_lines).strip()
                current_section = section_name
                current_lines = []
                matched = True
                break
        if not matched:
            current_lines.append(line)
    
    # Save last section
    if current_lines:
        sections[current_section] = '\n'.join(current_lines).strip()
    
    return sections


def extract_keywords_from_jd(jd_text: str) -> dict:
    """Extract key requirements from job description using regex patterns."""
    # Common tech skills
    tech_skills = [
        "python", "java", "javascript", "typescript", "react", "angular", "vue",
        "node", "express", "django", "flask", "fastapi", "spring", "docker",
        "kubernetes", "aws", "azure", "gcp", "sql", "nosql", "mongodb",
        "postgresql", "mysql", "redis", "git", "ci/cd", "jenkins", "terraform",
        "linux", "agile", "scrum", "rest", "api", "graphql", "microservices",
        "machine learning", "deep learning", "nlp", "tensorflow", "pytorch",
        "pandas", "numpy", "scikit-learn", "streamlit", "langchain",
        "html", "css", "tailwind", "figma", "excel", "power bi", "tableau",
        "c++", "c#", ".net", "rust", "go", "kotlin", "swift", "flutter",
        "react native", "next.js", "nest.js", "firebase", "supabase",
    ]
    
    jd_lower = jd_text.lower()
    
    found_skills = []
    for skill in tech_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', jd_lower):
            found_skills.append(skill)
    
    # Extract years of experience
    years_match = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience)?', jd_lower)
    min_years = int(years_match[0]) if years_match else 0
    
    # Extract education requirements
    education = []
    if re.search(r"(?i)(bachelor|b\.?s\.?|b\.?tech|b\.?e\.?)", jd_lower):
        education.append("Bachelor's")
    if re.search(r"(?i)(master|m\.?s\.?|m\.?tech|m\.?e\.?|mba)", jd_lower):
        education.append("Master's")
    if re.search(r"(?i)(ph\.?d|doctorate)", jd_lower):
        education.append("PhD")
    
    # Extract soft skills
    soft_skills = []
    soft_patterns = [
        "communication", "leadership", "teamwork", "problem solving",
        "analytical", "creative", "time management", "collaboration",
        "presentation", "mentoring", "stakeholder",
    ]
    for skill in soft_patterns:
        if skill in jd_lower:
            soft_skills.append(skill)
    
    return {
        "hard_skills": found_skills,
        "soft_skills": soft_skills,
        "min_years": min_years,
        "education": education,
    }
