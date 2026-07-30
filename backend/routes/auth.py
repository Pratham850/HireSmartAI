from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.recruiter import Recruiter
from schemas.auth import RecruiterRegister, RecruiterLogin, Token, RecruiterResponse
from services.auth_service import AuthService
from utils.dependencies import get_current_recruiter

router = APIRouter(prefix="/auth", tags=["1. Authentication"])


@router.post(
    "/register",
    response_model=RecruiterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new Recruiter account",
    description="Registers a new recruiter account with email, password, and full name."
)
async def register(
    data: RecruiterRegister,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    return await service.register_recruiter(data)


@router.post(
    "/login",
    response_model=Token,
    summary="Recruiter JWT Login",
    description="Authenticates recruiter credentials and returns JWT Access Token."
)
async def login(
    credentials: RecruiterLogin,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    return await service.login_recruiter(credentials)


@router.get(
    "/me",
    response_model=RecruiterResponse,
    summary="Get current recruiter profile",
    description="Returns details of the currently authenticated recruiter user."
)
async def get_me(
    recruiter: Recruiter = Depends(get_current_recruiter)
):
    return RecruiterResponse.model_validate(recruiter)
