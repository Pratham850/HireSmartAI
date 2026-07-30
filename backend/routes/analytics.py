from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.analytics import AnalyticsSummaryResponse
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["6. Recruitment Analytics"])


@router.get(
    "",
    response_model=AnalyticsSummaryResponse,
    summary="Get Recruitment Analytics & Metrics Summary",
    description="Returns aggregate KPI metrics including Top Skills, Department Wise breakdown, Average Match Score, Shortlisted & Rejected counts."
)
async def get_analytics(
    db: AsyncSession = Depends(get_db)
):
    service = AnalyticsService(db)
    return await service.get_analytics_summary()
