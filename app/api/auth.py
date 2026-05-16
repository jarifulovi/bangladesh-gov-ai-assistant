"""Auth routes for register/login."""

from fastapi import APIRouter, HTTPException, Header, status

from app.models.auth import AuthMeResponse, AuthResponse, LoginRequest, RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth")
service = AuthService()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> AuthResponse:
    print("[DEBUG] /auth/register payload:", payload)
    try:
        return await service.register(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest) -> AuthResponse:
    try:
        return await service.login(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.get("/me", response_model=AuthMeResponse)
async def me(x_session_id: str = Header(..., alias="X-Session-Id")) -> AuthMeResponse:
    try:
        return await service.me(x_session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(x_session_id: str = Header(..., alias="X-Session-Id")) -> None:
    await service.logout(x_session_id)
