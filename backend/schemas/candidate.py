from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class ExtractedCandidateData(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    education: Optional[List[Dict[str, Any]]] = []
    skills: Optional[List[str]] = []
    projects: Optional[List[Dict[str, Any]]] = []
    experience: Optional[List[Dict[str, Any]]] = []
    certifications: Optional[List[str]] = []


class CandidateResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    education: Optional[List[Dict[str, Any]]] = []
    skills: Optional[List[str]] = []
    projects: Optional[List[Dict[str, Any]]] = []
    experience: Optional[List[Dict[str, Any]]] = []
    certifications: Optional[List[str]] = []
    resume_pdf_path: str
    json_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateListResponse(BaseModel):
    total: int
    candidates: List[CandidateResponse]
