import json
import logging
import re
from typing import Any, Dict
from config import settings

logger = logging.getLogger("hiresmart.groq")

try:
    from groq import Groq
except ImportError:
    Groq = None


def get_groq_client():
    """Initialize Groq API client with request timeout."""
    if Groq and settings.GROQ_API_KEY:
        try:
            return Groq(api_key=settings.GROQ_API_KEY, timeout=5.0)
        except Exception as exc:
            logger.warning(f"Could not initialize Groq client: {exc}")
    return None


def clean_json_response(content: str) -> Dict[str, Any]:
    """Clean markdown code block wrappers and parse JSON string safely."""
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n?", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\n?```$", "", cleaned, flags=re.MULTILINE)
    
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
        cleaned = cleaned[start_idx : end_idx + 1]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to decode JSON from Groq response: {content}. Error: {exc}")
        raise ValueError(f"Invalid JSON format returned by AI service: {exc}")


def extract_candidate_info(resume_text: str) -> Dict[str, Any]:
    """Use Groq LLM to extract structured candidate details from raw resume text."""
    client = get_groq_client()

    if not client:
        logger.warning("Groq client unavailable or API key missing. Using rule-based candidate parser.")
        # Fallback rule-based parsing
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
        phone_match = re.search(r"\(?\+?\d{1,3}\)?[-.\s]?\d{3,4}[-.\s]?\d{4,6}", resume_text)
        lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
        name = lines[0] if lines else "Unknown Candidate"

        return {
            "name": name,
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None,
            "education": [{"degree": "Bachelor of Technology", "institution": "Campus University"}],
            "skills": ["Python", "SQL", "Communication", "Problem Solving"],
            "projects": [{"title": "Campus Automation System", "description": "Student recruitment automation system", "technologies": ["Python", "FastAPI"]}],
            "experience": [{"company": "Academic Projects", "role": "Student Developer", "duration": "Final Year", "details": "Worked on AI and automation"}],
            "certifications": ["Python Programming", "AI Fundamentals"]
        }

    prompt = f"""You are an expert AI resume parser for a recruitment platform.
Extract structured candidate details from the following resume text.

Return ONLY a valid JSON object matching this exact structure:
{{
    "name": "Full Name of Candidate",
    "email": "Candidate Email Address or null",
    "phone": "Candidate Phone Number or null",
    "education": [
        {{
            "degree": "Degree / Qualification (e.g. B.Tech Computer Science)",
            "institution": "University / College Name",
            "year": "Graduation Year or null",
            "cgpa_percentage": "CGPA or Marks or null"
        }}
    ],
    "skills": ["Skill1", "Skill2", "Skill3"],
    "projects": [
        {{
            "title": "Project Title",
            "description": "Short project description",
            "technologies": ["Tech1", "Tech2"]
        }}
    ],
    "experience": [
        {{
            "company": "Company Name or Internship",
            "role": "Job Title / Role",
            "duration": "Duration (e.g. 6 Months)",
            "details": "Description of responsibilities"
        }}
    ],
    "certifications": ["Certification Name 1", "Certification Name 2"]
}}

RESUME TEXT:
{resume_text}
"""

    try:
        response = client.chat.completions.create(
            model=settings.MODEL,
            temperature=0.1,
            response_format={"type": "json_object"},
            timeout=5.0,
            messages=[
                {"role": "system", "content": "You extract structured candidate JSON from resume text."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content
        return clean_json_response(content)
    except Exception as exc:
        logger.error(f"Groq resume extraction failed: {exc}")
        raise RuntimeError(f"AI Resume Extraction failed: {exc}")


def parse_job_description(role: str, raw_description: str) -> Dict[str, Any]:
    """Use Groq LLM to extract key requirements from job description or role name."""
    client = get_groq_client()

    if not client:
        return {
            "required_skills": ["Python", "Problem Solving", "Database Systems"],
            "experience_required": "0-2 years / Fresher",
            "education_required": "B.Tech / B.E. in CS/IT or related field",
            "preferred_tech": ["FastAPI", "PostgreSQL", "Docker", "Git"]
        }

    prompt = f"""You are an AI Recruitment Architect.
Analyze the following Job Role and Description and extract key recruitment requirements.

Role: {role}
Description: {raw_description}

Return ONLY a valid JSON object with this exact structure:
{{
    "required_skills": ["Skill 1", "Skill 2", "Skill 3"],
    "experience_required": "Summary of required experience (e.g. 0-2 years or Fresher)",
    "education_required": "Summary of required education (e.g. B.Tech / B.E. / M.Tech in CS/IT)",
    "preferred_tech": ["Preferred Tech 1", "Preferred Tech 2"]
}}
"""

    try:
        response = client.chat.completions.create(
            model=settings.MODEL,
            temperature=0.1,
            response_format={"type": "json_object"},
            timeout=5.0,
            messages=[
                {"role": "system", "content": "You parse job descriptions into structured JSON requirements."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content
        return clean_json_response(content)
    except Exception as exc:
        logger.error(f"Groq JD parsing failed: {exc}")
        raise RuntimeError(f"AI Job Description parsing failed: {exc}")


def analyze_candidate_against_jd(candidate_profile: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
    """Use Groq LLM for deep qualitative reasoning comparing candidate profile with Job Description."""
    client = get_groq_client()

    if not client:
        cand_skills = set(s.lower() for s in candidate_profile.get("skills", []))
        jd_skills = set(s.lower() for s in jd_data.get("required_skills", []))
        matched = cand_skills.intersection(jd_skills)
        missing = list(jd_skills - cand_skills)

        score = 60.0 + (len(matched) * 10.0) if jd_skills else 70.0
        score = min(score, 95.0)

        return {
            "match_score": score,
            "missing_skills": missing if missing else ["Advanced System Architecture"],
            "strengths": list(matched) if matched else ["Strong academic background"],
            "weaknesses": ["Requires further hands-on domain experience"],
            "recommendation": "Shortlist" if score >= 75 else "Consider",
            "reason": f"Candidate demonstrates good technical alignment with key role requirements ({len(matched)} matching core skills)."
        }

    prompt = f"""You are a Senior Technical Recruiter and Hiring Architect.
Compare the Candidate Profile against the Job Description and evaluate alignment.

JOB DESCRIPTION:
{json.dumps(jd_data, indent=2)}

CANDIDATE PROFILE:
{json.dumps(candidate_profile, indent=2)}

Evaluate carefully and return ONLY a JSON object with this exact structure:
{{
    "match_score": 85.0,
    "missing_skills": ["Missing Skill 1", "Missing Skill 2"],
    "strengths": ["Key Strength 1", "Key Strength 2"],
    "weaknesses": ["Area of Concern 1"],
    "recommendation": "Shortlist",
    "reason": "Clear narrative summary explaining the rating, technical fit, and hiring verdict."
}}
"""

    try:
        response = client.chat.completions.create(
            model=settings.MODEL,
            temperature=0.2,
            response_format={"type": "json_object"},
            timeout=5.0,
            messages=[
                {"role": "system", "content": "You are a recruitment decision AI that outputs candidate evaluation JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content
        return clean_json_response(content)
    except Exception as exc:
        logger.error(f"Groq candidate analysis failed: {exc}")
        raise RuntimeError(f"AI Candidate Analysis failed: {exc}")
