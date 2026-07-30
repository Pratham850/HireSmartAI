from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.job_description import JobDescriptionCreate, JobDescriptionResponse
from services.job_service import JobService

router = APIRouter(tags=["4. Job Description APIs"])


@router.post(
    "/job-description",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create & AI Extract Job Description Requirements",
    description="""
    Accepts predefined job role (Backend Developer, Full Stack Developer, Data Analyst, AIML Engineer, etc.)
    or custom Job Description text, extracts required skills, experience, education, preferred technologies via Groq AI,
    and persists in database.
    """
)
async def create_job_description(
    data: JobDescriptionCreate,
    db: AsyncSession = Depends(get_db)
):
    service = JobService(db)
    return await service.create_job_description(data)


@router.get(
    "/job-descriptions",
    response_model=List[JobDescriptionResponse],
    summary="List all created Job Descriptions",
    description="Returns list of all job roles and parsed requirements."
)
async def get_all_job_descriptions(
    db: AsyncSession = Depends(get_db)
):
    service = JobService(db)
    return await service.get_all_job_descriptions()
