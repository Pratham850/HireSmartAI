from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class RecruiterRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class RecruiterLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RecruiterResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
