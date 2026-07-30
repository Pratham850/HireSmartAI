from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.recruiter import Recruiter
from schemas.auth import RecruiterRegister, RecruiterLogin, Token, RecruiterResponse
from utils.security import hash_password, verify_password, create_access_token


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_recruiter(self, data: RecruiterRegister) -> RecruiterResponse:
        stmt = select(Recruiter).where(Recruiter.email == data.email)
        result = await self.db.execute(stmt)
        existing = result.scalars().first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A recruiter account with this email already exists"
            )

        hashed_pwd = hash_password(data.password)
        recruiter = Recruiter(
            email=data.email,
            hashed_password=hashed_pwd,
            full_name=data.full_name
        )
        self.db.add(recruiter)
        await self.db.flush()
        await self.db.refresh(recruiter)
        return RecruiterResponse.model_validate(recruiter)

    async def login_recruiter(self, credentials: RecruiterLogin) -> Token:
        stmt = select(Recruiter).where(Recruiter.email == credentials.email)
        result = await self.db.execute(stmt)
        recruiter = result.scalars().first()

        if not recruiter or not verify_password(credentials.password, recruiter.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        access_token = create_access_token(data={"sub": str(recruiter.id), "email": recruiter.email})
        return Token(access_token=access_token, token_type="bearer")
