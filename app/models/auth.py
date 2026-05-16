"""Auth request/response schemas."""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class AuthResponse(BaseModel):
    user_id: str
    session_id: str


class AuthMeResponse(BaseModel):
    user_id: str
    email: str
    full_name: str | None = None
    session_id: str
