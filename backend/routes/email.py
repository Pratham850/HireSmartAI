from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.email import SendEmailRequest, SendEmailResponse
from services.email_service import EmailService

router = APIRouter(prefix="/email", tags=["8. Email Notifications"])


@router.post(
    "/send-shortlisted",
    response_model=SendEmailResponse,
    summary="Send SMTP Notification Emails to Shortlisted Candidates",
    description="Sends interview notification emails via SMTP to all candidates shortlisted for a given job role."
)
async def send_shortlisted_emails(
    request: SendEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    service = EmailService(db)
    return await service.send_shortlist_emails(request)
