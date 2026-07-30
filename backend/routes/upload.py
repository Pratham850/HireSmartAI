from fastapi import APIRouter, Depends, File, UploadFile, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.candidate import CandidateResponse
from services.resume_service import ResumeService

router = APIRouter(tags=["2. Resume Upload"])


@router.post(
    "/upload-resume",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF Resume & Extract Candidate Profile using AI",
    description="""
    Receives PDF resume file (from UiPath robot or recruiter UI), extracts text using PyMuPDF,
    invokes Groq AI to extract structured details (Name, Email, Phone, Education, Skills, Projects, Experience, Certifications),
    stores profile in PostgreSQL database, saves JSON copy in uploads/json, and returns Candidate JSON.
    """
)
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file:
        raise HTTPException(status_code=400, detail="No PDF file uploaded")
    
    service = ResumeService(db)
    return await service.process_and_save_resume(file)
