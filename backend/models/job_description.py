from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, DateTime, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    experience_required: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    education_required: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preferred_tech: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    analysis_results = relationship("AnalysisResult", back_populates="job_description", cascade="all, delete-orphan")
