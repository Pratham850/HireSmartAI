from typing import Dict, List
from pydantic import BaseModel


class SkillCount(BaseModel):
    skill: str
    count: int


class DepartmentCount(BaseModel):
    department: str
    count: int


class AnalyticsSummaryResponse(BaseModel):
    total_candidates: int
    total_job_descriptions: int
    total_analyses_run: int
    average_match_score: float
    selected_shortlisted_count: int
    rejected_count: int
    considered_count: int
    top_skills: List[SkillCount]
    department_wise: List[DepartmentCount]
