import os
import uuid
import json
import logging
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.candidate import Candidate
from schemas.candidate import CandidateResponse
from utils.pdf_parser import extract_text_from_pdf
from utils.groq_client import extract_candidate_info
from config import settings

logger = logging.getLogger("hiresmart.resume_service")

try:
    import aiofiles
except ImportError:
    aiofiles = None


class ResumeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_and_save_resume(self, file: UploadFile) -> CandidateResponse:
        """Process incoming PDF resume, run AI extraction, store DB record and JSON archive."""
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF resume files are accepted"
            )

        unique_id = uuid.uuid4().hex[:8]
        safe_filename = f"{unique_id}_{file.filename}"
        pdf_path = os.path.join(settings.PDF_DIR, safe_filename)

        # Save PDF to disk
        try:
            content = await file.read()
            if aiofiles:
                async with aiofiles.open(pdf_path, "wb") as out_file:
                    await out_file.write(content)
            else:
                with open(pdf_path, "wb") as out_file:
                    out_file.write(content)
        except Exception as exc:
            logger.error(f"Failed to save PDF file: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to write uploaded file to disk: {exc}"
            )

        # Step 1: Extract plain text using PyMuPDF / Fallback
        try:
            raw_text = extract_text_from_pdf(pdf_path)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to extract text from PDF: {exc}"
            )

        # Step 2: Extract candidate information using Groq AI
        try:
            extracted_data = extract_candidate_info(raw_text)
        except Exception as exc:
            logger.error(f"Groq extraction failed: {exc}")
            extracted_data = {
                "name": file.filename.rsplit(".", 1)[0].replace("_", " ").title(),
                "email": None,
                "phone": None,
                "education": [],
                "skills": [],
                "projects": [],
                "experience": [],
                "certifications": []
            }

        candidate_name = extracted_data.get("name") or "Unknown Candidate"
        candidate_email = extracted_data.get("email")
        candidate_phone = extracted_data.get("phone")

        # Step 3: Save Candidate profile in PostgreSQL / SQLite DB
        candidate = Candidate(
            name=candidate_name,
            email=candidate_email,
            phone=candidate_phone,
            education=extracted_data.get("education", []),
            skills=extracted_data.get("skills", []),
            projects=extracted_data.get("projects", []),
            experience=extracted_data.get("experience", []),
            certifications=extracted_data.get("certifications", []),
            raw_text=raw_text,
            resume_pdf_path=pdf_path,
            json_path=None
        )
        self.db.add(candidate)
        await self.db.flush()
        await self.db.refresh(candidate)

        # Step 4: Save JSON copy in uploads/json
        json_filename = f"candidate_{candidate.id}.json"
        json_path = os.path.join(settings.JSON_DIR, json_filename)
        
        json_payload = {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "education": candidate.education,
            "skills": candidate.skills,
            "projects": candidate.projects,
            "experience": candidate.experience,
            "certifications": candidate.certifications,
            "resume_pdf_path": candidate.resume_pdf_path,
            "created_at": candidate.created_at.isoformat()
        }

        try:
            formatted_json = json.dumps(json_payload, indent=2)
            if aiofiles:
                async with aiofiles.open(json_path, "w", encoding="utf-8") as json_file:
                    await json_file.write(formatted_json)
            else:
                with open(json_path, "w", encoding="utf-8") as json_file:
                    json_file.write(formatted_json)
            
            candidate.json_path = json_path
            await self.db.flush()
            await self.db.refresh(candidate)
        except Exception as exc:
            logger.error(f"Failed to write JSON copy for candidate {candidate.id}: {exc}")

        return CandidateResponse.model_validate(candidate)
