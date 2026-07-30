import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import init_db
from routes import (
    auth_router,
    upload_router,
    candidates_router,
    job_router,
    analyze_router,
    analytics_router,
    reports_router,
    email_router,
)

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("hiresmart.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for application startup and shutdown."""
    logger.info("Initializing HireSmart AI Database tables...")
    try:
        await init_db()
        logger.info("Database initialization successful.")
    except Exception as exc:
        logger.error(f"Database initialization failed: {exc}")
    yield
    logger.info("Shutting down HireSmart AI Application...")


app = FastAPI(
    title="HireSmart AI - Campus Recruitment Automation API",
    description="""
    ## Production Backend for HireSmart AI
    AI-powered Campus Recruitment Automation System supporting:
    - **Google Drive / UiPath Robot Integration**: Automated resume PDF ingestion.
    - **AI Candidate Extraction**: Resume text parsing using PyMuPDF & Groq LLM (`llama-3.3-70b-versatile`).
    - **Job Description Analysis**: Automated extraction of skills, experience, and tech requirements.
    - **Hybrid AI Ranking**: Sentence Transformers embedding vector cosine similarity combined with Groq reasoning.
    - **Recruitment Analytics**: Top skills, department metrics, average scores, and candidate funnel statistics.
    - **Report Export**: Downloadable Excel (`.xlsx`), CSV (`.csv`), and JSON (`.json`) recruitment summaries.
    - **SMTP Email Notifications**: Automated interview invites for shortlisted candidates.
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception occurred at {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred.",
            "error_type": type(exc).__name__,
            "message": str(exc)
        }
    )


# Register Routers
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(candidates_router)
app.include_router(job_router)
app.include_router(analyze_router)
app.include_router(analytics_router)
app.include_router(reports_router)
app.include_router(email_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "message": "HireSmart AI Campus Recruitment Backend Running 🚀",
        "swagger_docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
