from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class JobDescriptionCreate(BaseModel):
    role: Optional[str] = None
    job_description: Optional[str] = None


class ParsedJobDescription(BaseModel):
    required_skills: List[str] = []
    experience_required: str = ""
    education_required: str = ""
    preferred_tech: List[str] = []


class JobDescriptionResponse(BaseModel):
    id: int
    role: str
    raw_description: str
    required_skills: Optional[List[str]] = []
    experience_required: Optional[str] = None
    education_required: Optional[str] = None
    preferred_tech: Optional[List[str]] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
