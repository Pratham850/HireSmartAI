from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from schemas.candidate import CandidateResponse


class AnalyzeRequest(BaseModel):
    job_description_id: Optional[int] = None
    role: Optional[str] = None
    job_description: Optional[str] = None


class AnalysisResultResponse(BaseModel):
    id: int
    candidate_id: int
    job_description_id: int
    match_score: float
    missing_skills: Optional[List[str]] = []
    strengths: Optional[List[str]] = []
    weaknesses: Optional[List[str]] = []
    recommendation: str
    reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RankedCandidateResponse(BaseModel):
    candidate: CandidateResponse
    match_score: float
    missing_skills: List[str] = []
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendation: str
    reason: str


class RankingListResponse(BaseModel):
    job_description_id: int
    role: str
    total_candidates_analyzed: int
    rankings: List[RankedCandidateResponse]
