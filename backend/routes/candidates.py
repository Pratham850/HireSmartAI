from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.candidate import CandidateResponse, CandidateListResponse
from services.candidate_service import CandidateService

router = APIRouter(tags=["3. Candidate APIs"])


@router.get(
    "/candidates",
    response_model=CandidateListResponse,
    summary="Get all stored candidate profiles",
    description="Retrieves candidate profiles with optional search filtering and pagination."
)
async def get_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="Search candidate name or email"),
    db: AsyncSession = Depends(get_db)
):
    service = CandidateService(db)
    return await service.get_all_candidates(skip=skip, limit=limit, search=search)


@router.get(
    "/candidate/{id}",
    response_model=CandidateResponse,
    summary="Get specific candidate profile by ID",
    description="Fetches detailed structured profile of candidate by database ID."
)
async def get_candidate_by_id(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    service = CandidateService(db)
    return await service.get_candidate_by_id(id)


@router.delete(
    "/candidate/{id}",
    summary="Delete candidate by ID",
    description="Deletes candidate record, associated PDF resume file, JSON archive, and analysis results."
)
async def delete_candidate(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    service = CandidateService(db)
    return await service.delete_candidate(id)
