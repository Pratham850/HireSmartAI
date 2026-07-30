import os
import logging
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from models.candidate import Candidate
from schemas.candidate import CandidateResponse, CandidateListResponse

logger = logging.getLogger("hiresmart.candidate_service")


class CandidateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_candidates(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> CandidateListResponse:
        query = select(Candidate)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Candidate.name.ilike(search_pattern)) |
                (Candidate.email.ilike(search_pattern))
            )
            
        count_stmt = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one_or_none() or 0

        stmt = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        candidates = result.scalars().all()

        candidate_responses = [CandidateResponse.model_validate(c) for c in candidates]
        return CandidateListResponse(total=total, candidates=candidate_responses)

    async def get_candidate_by_id(self, candidate_id: int) -> CandidateResponse:
        stmt = select(Candidate).where(Candidate.id == candidate_id)
        result = await self.db.execute(stmt)
        candidate = result.scalars().first()
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with ID {candidate_id} not found"
            )
        return CandidateResponse.model_validate(candidate)

    async def delete_candidate(self, candidate_id: int) -> dict:
        stmt = select(Candidate).where(Candidate.id == candidate_id)
        result = await self.db.execute(stmt)
        candidate = result.scalars().first()
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with ID {candidate_id} not found"
            )

        # Cleanup files on disk
        if candidate.resume_pdf_path and os.path.exists(candidate.resume_pdf_path):
            try:
                os.remove(candidate.resume_pdf_path)
            except Exception as exc:
                logger.warning(f"Could not remove PDF file {candidate.resume_pdf_path}: {exc}")

        if candidate.json_path and os.path.exists(candidate.json_path):
            try:
                os.remove(candidate.json_path)
            except Exception as exc:
                logger.warning(f"Could not remove JSON file {candidate.json_path}: {exc}")

        await self.db.delete(candidate)
        await self.db.flush()
        return {"message": f"Candidate with ID {candidate_id} successfully deleted"}
