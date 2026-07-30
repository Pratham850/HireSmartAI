from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import String, Text, DateTime, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    education: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    skills: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    projects: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    experience: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    certifications: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resume_pdf_path: Mapped[str] = mapped_column(String(500), nullable=False)
    json_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    analysis_results = relationship("AnalysisResult", back_populates="candidate", cascade="all, delete-orphan")
