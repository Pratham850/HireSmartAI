import logging
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.job_description import JobDescription
from schemas.job_description import JobDescriptionCreate, JobDescriptionResponse
from utils.groq_client import parse_job_description

logger = logging.getLogger("hiresmart.job_service")

# Default Job Descriptions for standard roles if user only provides role name
DEFAULT_ROLE_DESCRIPTIONS = {
    "Backend Developer": "Seeking a Backend Developer skilled in Python, FastAPI, Django, PostgreSQL, REST APIs, Microservices, Redis, Docker, and Git.",
    "Full Stack Developer": "Seeking a Full Stack Developer proficient in React, Node.js, Python, TypeScript, HTML/CSS, PostgreSQL, Docker, and RESTful APIs.",
    "Data Analyst": "Seeking a Data Analyst experienced in Python, SQL, Pandas, NumPy, Data Visualization (Tableau/PowerBI), Statistics, and Excel.",
    "AIML Engineer": "Seeking an AI/ML Engineer with expertise in Python, PyTorch, TensorFlow, Scikit-Learn, NLP, LLMs, Vector Databases, and MLOps."
}


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job_description(self, data: JobDescriptionCreate) -> JobDescriptionResponse:
        role = data.role or "Custom Role"
        raw_description = data.job_description

        if not raw_description and role in DEFAULT_ROLE_DESCRIPTIONS:
            raw_description = DEFAULT_ROLE_DESCRIPTIONS[role]
        elif not raw_description:
            raw_description = f"Job vacancy for {role}. Seeking qualified candidates with relevant technical skills, educational background, and project experience."

        # Run AI extraction to parse requirements
        try:
            parsed_info = parse_job_description(role, raw_description)
        except Exception as exc:
            logger.error(f"Failed to parse JD via AI: {exc}")
            parsed_info = {
                "required_skills": [role],
                "experience_required": "Not specified",
                "education_required": "Bachelor's degree or equivalent",
                "preferred_tech": []
            }

        job_desc = JobDescription(
            role=role,
            raw_description=raw_description,
            required_skills=parsed_info.get("required_skills", []),
            experience_required=parsed_info.get("experience_required"),
            education_required=parsed_info.get("education_required"),
            preferred_tech=parsed_info.get("preferred_tech", [])
        )
        self.db.add(job_desc)
        await self.db.flush()
        await self.db.refresh(job_desc)

        return JobDescriptionResponse.model_validate(job_desc)

    async def get_all_job_descriptions(self) -> List[JobDescriptionResponse]:
        stmt = select(JobDescription).order_by(JobDescription.created_at.desc())
        result = await self.db.execute(stmt)
        records = result.scalars().all()
        return [JobDescriptionResponse.model_validate(j) for j in records]

    async def get_job_description_by_id(self, jd_id: int) -> JobDescriptionResponse:
        stmt = select(JobDescription).where(JobDescription.id == jd_id)
        result = await self.db.execute(stmt)
        jd = result.scalars().first()
        if not jd:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job Description with ID {jd_id} not found"
            )
        return JobDescriptionResponse.model_validate(jd)
