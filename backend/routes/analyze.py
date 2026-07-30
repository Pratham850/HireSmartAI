from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.analysis import AnalyzeRequest, RankingListResponse
from services.ranking_service import RankingService

router = APIRouter(tags=["5. AI Ranking Engine"])


@router.post(
    "/analyze",
    response_model=RankingListResponse,
    summary="Compare ALL candidates against Job Description and return AI Ranked List",
    description="""
    Compares all stored candidate profiles against target Job Description using Sentence Transformers embeddings (cosine similarity)
    and Groq AI qualitative reasoning. Generates Match Score, Missing Skills, Strengths, Weaknesses, Recommendation (Shortlist/Consider/Reject),
    Reason narrative, and returns sorted candidate list.
    """
)
async def analyze_and_rank(
    request: AnalyzeRequest,
    db: AsyncSession = Depends(get_db)
):
    service = RankingService(db)
    return await service.analyze_and_rank_candidates(request)
