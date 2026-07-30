from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, DateTime, JSON, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_description_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    missing_skills: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    strengths: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    recommendation: Mapped[str] = mapped_column(String(50), nullable=False, default="Consider")
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    candidate = relationship("Candidate", back_populates="analysis_results")
    job_description = relationship("JobDescription", back_populates="analysis_results")
