import logging
from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.candidate import Candidate
from models.job_description import JobDescription
from models.analysis_result import AnalysisResult
from schemas.analysis import AnalyzeRequest, RankingListResponse, RankedCandidateResponse
from schemas.candidate import CandidateResponse
from services.job_service import JobService
from utils.embedding_utils import compute_similarity_score
from utils.groq_client import analyze_candidate_against_jd

logger = logging.getLogger("hiresmart.ranking_service")


class RankingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_service = JobService(db)

    async def analyze_and_rank_candidates(self, request: AnalyzeRequest) -> RankingListResponse:
        # Step 1: Resolve Job Description
        jd_model = None
        if request.job_description_id:
            stmt = select(JobDescription).where(JobDescription.id == request.job_description_id)
            result = await self.db.execute(stmt)
            jd_model = result.scalars().first()

        if not jd_model:
            # Create a new Job Description entry
            create_payload = await self.job_service.create_job_description(
                request_to_create := type("Obj", (), {
                    "role": request.role or "Target Role",
                    "job_description": request.job_description
                })()
            )
            stmt = select(JobDescription).where(JobDescription.id == create_payload.id)
            result = await self.db.execute(stmt)
            jd_model = result.scalars().first()

        # Step 2: Fetch all stored candidates
        cand_stmt = select(Candidate)
        cand_result = await self.db.execute(cand_stmt)
        candidates = cand_result.scalars().all()

        if not candidates:
            return RankingListResponse(
                job_description_id=jd_model.id,
                role=jd_model.role,
                total_candidates_analyzed=0,
                rankings=[]
            )

        jd_text = f"Role: {jd_model.role}\nDescription: {jd_model.raw_description}\nRequired Skills: {', '.join(jd_model.required_skills or [])}"
        jd_dict = {
            "role": jd_model.role,
            "raw_description": jd_model.raw_description,
            "required_skills": jd_model.required_skills or [],
            "experience_required": jd_model.experience_required,
            "education_required": jd_model.education_required,
            "preferred_tech": jd_model.preferred_tech or []
        }

        ranked_items = []

        # Step 3: Analyze each candidate
        for candidate in candidates:
            candidate_text = f"Candidate: {candidate.name}\nSkills: {', '.join(candidate.skills or [])}\nText: {candidate.raw_text or ''}"
            
            # Sentence Transformer Embedding similarity (0-100)
            try:
                vector_sim = compute_similarity_score(candidate_text, jd_text)
            except Exception as exc:
                logger.warning(f"Vector similarity error for candidate {candidate.id}: {exc}")
                vector_sim = 50.0

            # Groq Reasoning
            candidate_profile = {
                "name": candidate.name,
                "email": candidate.email,
                "skills": candidate.skills or [],
                "education": candidate.education or [],
                "experience": candidate.experience or [],
                "projects": candidate.projects or [],
                "certifications": candidate.certifications or []
            }

            try:
                ai_eval = analyze_candidate_against_jd(candidate_profile, jd_dict)
            except Exception as exc:
                logger.error(f"AI evaluation failed for candidate {candidate.id}: {exc}")
                ai_eval = {
                    "match_score": vector_sim,
                    "missing_skills": jd_model.required_skills or [],
                    "strengths": ["Profile stored in system"],
                    "weaknesses": ["Detailed AI evaluation pending"],
                    "recommendation": "Consider" if vector_sim >= 50 else "Reject",
                    "reason": "Evaluated primarily via vector similarity due to AI provider throttling."
                }

            groq_score = float(ai_eval.get("match_score", vector_sim))
            # Hybrid match score calculation
            final_match_score = round(0.35 * vector_sim + 0.65 * groq_score, 2)
            final_match_score = min(max(final_match_score, 0.0), 100.0)

            recommendation = ai_eval.get("recommendation", "Consider")
            if final_match_score >= 75.0:
                recommendation = "Shortlist"
            elif final_match_score < 45.0:
                recommendation = "Reject"

            # Check if AnalysisResult already exists
            ar_stmt = select(AnalysisResult).where(
                AnalysisResult.candidate_id == candidate.id,
                AnalysisResult.job_description_id == jd_model.id
            )
            ar_res = await self.db.execute(ar_stmt)
            existing_ar = ar_res.scalars().first()

            if existing_ar:
                existing_ar.match_score = final_match_score
                existing_ar.missing_skills = ai_eval.get("missing_skills", [])
                existing_ar.strengths = ai_eval.get("strengths", [])
                existing_ar.weaknesses = ai_eval.get("weaknesses", [])
                existing_ar.recommendation = recommendation
                existing_ar.reason = ai_eval.get("reason", "")
            else:
                new_ar = AnalysisResult(
                    candidate_id=candidate.id,
                    job_description_id=jd_model.id,
                    match_score=final_match_score,
                    missing_skills=ai_eval.get("missing_skills", []),
                    strengths=ai_eval.get("strengths", []),
                    weaknesses=ai_eval.get("weaknesses", []),
                    recommendation=recommendation,
                    reason=ai_eval.get("reason", "")
                )
                self.db.add(new_ar)

            ranked_items.append(
                RankedCandidateResponse(
                    candidate=CandidateResponse.model_validate(candidate),
                    match_score=final_match_score,
                    missing_skills=ai_eval.get("missing_skills", []),
                    strengths=ai_eval.get("strengths", []),
                    weaknesses=ai_eval.get("weaknesses", []),
                    recommendation=recommendation,
                    reason=ai_eval.get("reason", "Profile evaluated successfully")
                )
            )

        await self.db.flush()

        # Sort candidate rankings by match score descending
        ranked_items.sort(key=lambda x: x.match_score, reverse=True)

        return RankingListResponse(
            job_description_id=jd_model.id,
            role=jd_model.role,
            total_candidates_analyzed=len(ranked_items),
            rankings=ranked_items
        )
