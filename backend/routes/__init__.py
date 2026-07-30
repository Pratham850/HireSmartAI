from routes.auth import router as auth_router
from routes.upload import router as upload_router
from routes.candidates import router as candidates_router
from routes.job_description import router as job_router
from routes.analyze import router as analyze_router
from routes.analytics import router as analytics_router
from routes.reports import router as reports_router
from routes.email import router as email_router

__all__ = [
    "auth_router",
    "upload_router",
    "candidates_router",
    "job_router",
    "analyze_router",
    "analytics_router",
    "reports_router",
    "email_router",
]
