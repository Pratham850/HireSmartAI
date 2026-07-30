from collections import Counter
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from models.candidate import Candidate
from models.job_description import JobDescription
from models.analysis_result import AnalysisResult
from schemas.analytics import AnalyticsSummaryResponse, SkillCount, DepartmentCount


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_analytics_summary(self) -> AnalyticsSummaryResponse:
        # Candidate Count
        c_stmt = select(func.count(Candidate.id))
        total_candidates = (await self.db.execute(c_stmt)).scalar_one_or_none() or 0

        # Job Descriptions Count
        j_stmt = select(func.count(JobDescription.id))
        total_jds = (await self.db.execute(j_stmt)).scalar_one_or_none() or 0

        # Analysis Count & Average Score
        a_stmt = select(
            func.count(AnalysisResult.id),
            func.avg(AnalysisResult.match_score)
        )
        a_res = (await self.db.execute(a_stmt)).first()
        total_analyses = a_res[0] if a_res else 0
        avg_score = float(a_res[1]) if a_res and a_res[1] is not None else 0.0

        # Status counts
        shortlisted_stmt = select(func.count(AnalysisResult.id)).where(AnalysisResult.recommendation == "Shortlist")
        shortlisted_count = (await self.db.execute(shortlisted_stmt)).scalar_one_or_none() or 0

        rejected_stmt = select(func.count(AnalysisResult.id)).where(AnalysisResult.recommendation == "Reject")
        rejected_count = (await self.db.execute(rejected_stmt)).scalar_one_or_none() or 0

        considered_stmt = select(func.count(AnalysisResult.id)).where(AnalysisResult.recommendation == "Consider")
        considered_count = (await self.db.execute(considered_stmt)).scalar_one_or_none() or 0

        # Extract top skills and department/education breakdown from candidates
        cand_stmt = select(Candidate)
        cand_list = (await self.db.execute(cand_stmt)).scalars().all()

        skill_counter = Counter()
        dept_counter = Counter()

        for cand in cand_list:
            if cand.skills:
                for skill in cand.skills:
                    if skill and isinstance(skill, str):
                        skill_counter[skill.strip().title()] += 1

            if cand.education and isinstance(cand.education, list):
                for edu in cand.education:
                    if isinstance(edu, dict):
                        degree = edu.get("degree") or "General Engineering"
                        dept_counter[degree.strip().title()] += 1
            else:
                dept_counter["General / Unspecified"] += 1

        top_skills = [
            SkillCount(skill=s, count=c)
            for s, c in skill_counter.most_common(10)
        ]

        department_wise = [
            DepartmentCount(department=d, count=c)
            for d, c in dept_counter.most_common(10)
        ]

        return AnalyticsSummaryResponse(
            total_candidates=total_candidates,
            total_job_descriptions=total_jds,
            total_analyses_run=total_analyses,
            average_match_score=round(avg_score, 2),
            selected_shortlisted_count=shortlisted_count,
            rejected_count=rejected_count,
            considered_count=considered_count,
            top_skills=top_skills,
            department_wise=department_wise
        )
