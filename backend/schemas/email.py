from typing import List, Optional
from pydantic import BaseModel, EmailStr


class SendEmailRequest(BaseModel):
    job_description_id: Optional[int] = None
    candidate_ids: Optional[List[int]] = None
    custom_subject: Optional[str] = None
    custom_message: Optional[str] = None


class EmailResult(BaseModel):
    candidate_id: int
    name: str
    email: str
    status: str
    message: str


class SendEmailResponse(BaseModel):
    total_emails_attempted: int
    successful_count: int
    failed_count: int
    results: List[EmailResult]
