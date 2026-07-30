import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.candidate import Candidate
from models.analysis_result import AnalysisResult
from models.job_description import JobDescription
from schemas.email import SendEmailRequest, SendEmailResponse, EmailResult
from config import settings

logger = logging.getLogger("hiresmart.email_service")


class EmailService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_shortlist_emails(self, request: SendEmailRequest) -> SendEmailResponse:
        results: List[EmailResult] = []

        # Find candidates to email
        if request.candidate_ids:
            cand_stmt = select(Candidate).where(Candidate.id.in_(request.candidate_ids))
            candidates = (await self.db.execute(cand_stmt)).scalars().all()
        else:
            query = select(Candidate).join(
                AnalysisResult, Candidate.id == AnalysisResult.candidate_id
            ).where(AnalysisResult.recommendation == "Shortlist")
            
            if request.job_description_id:
                query = query.where(AnalysisResult.job_description_id == request.job_description_id)
                
            candidates = (await self.db.execute(query)).scalars().all()

        if not candidates:
            return SendEmailResponse(
                total_emails_attempted=0,
                successful_count=0,
                failed_count=0,
                results=[]
            )

        success_count = 0
        failed_count = 0

        for cand in candidates:
            if not cand.email or "@" not in cand.email:
                results.append(
                    EmailResult(
                        candidate_id=cand.id,
                        name=cand.name,
                        email=cand.email or "None",
                        status="Failed",
                        message="Missing valid email address"
                    )
                )
                failed_count += 1
                continue

            subject = request.custom_subject or f"Congratulations {cand.name}! You are Shortlisted for HireSmart AI Campus Drive"
            body = request.custom_message or f"""Dear {cand.name},

We are pleased to inform you that your profile has been SHORTLISTED for the upcoming recruitment round at HireSmart AI Campus Placement Drive.

Candidate ID: {cand.id}
Primary Skills Identified: {', '.join(cand.skills or [])}

Our recruitment team will follow up shortly with details regarding your technical interview schedule.

Best Regards,
Recruitment Team
HireSmart AI Automation System
"""

            # Attempt SMTP send (or mock mode if SMTP settings unconfigured)
            try:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    msg = MIMEMultipart()
                    msg["From"] = settings.EMAIL_FROM
                    msg["To"] = cand.email
                    msg["Subject"] = subject
                    msg.attach(MIMEText(body, "plain"))

                    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                        server.starttls()
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                        server.send_message(msg)

                    status_str = "Sent"
                    msg_str = "Email delivered successfully via SMTP"
                else:
                    status_str = "Simulated"
                    msg_str = f"Simulated dispatch to {cand.email} (Configure SMTP_USER & SMTP_PASSWORD in .env for production SMTP)"

                results.append(
                    EmailResult(
                        candidate_id=cand.id,
                        name=cand.name,
                        email=cand.email,
                        status=status_str,
                        message=msg_str
                    )
                )
                success_count += 1

            except Exception as exc:
                logger.error(f"Failed sending email to {cand.email}: {exc}")
                results.append(
                    EmailResult(
                        candidate_id=cand.id,
                        name=cand.name,
                        email=cand.email,
                        status="Failed",
                        message=f"SMTP dispatch error: {exc}"
                    )
                )
                failed_count += 1

        return SendEmailResponse(
            total_emails_attempted=len(candidates),
            successful_count=success_count,
            failed_count=failed_count,
            results=results
        )
