"""History routes for threads and messages."""

from fastapi import APIRouter, Header, HTTPException, status

from app.models.history import MessageResponse, ThreadCreateRequest, ThreadRenameRequest, ThreadResponse
from app.services.auth_service import AuthService
from app.services.history_service import HistoryService

router = APIRouter(prefix="/history")
service = HistoryService()
auth_service = AuthService()


@router.post("/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    payload: ThreadCreateRequest,
    x_session_id: str = Header(..., alias="X-Session-Id"),
) -> ThreadResponse:
    try:
        session = await auth_service.validate_session(x_session_id)
        return await service.create_thread(session["user_id"], payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/threads", response_model=list[ThreadResponse])
async def list_threads(x_session_id: str = Header(..., alias="X-Session-Id")) -> list[ThreadResponse]:
    try:
        session = await auth_service.validate_session(x_session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return await service.list_threads(session["user_id"])


@router.patch("/threads/{thread_id}", response_model=ThreadResponse)
async def rename_thread(
    thread_id: str,
    payload: ThreadRenameRequest,
    x_session_id: str = Header(..., alias="X-Session-Id"),
) -> ThreadResponse:
    try:
        session = await auth_service.validate_session(x_session_id)
        return await service.rename_thread(session["user_id"], thread_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.get("/threads/{thread_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    thread_id: str,
    x_session_id: str = Header(..., alias="X-Session-Id"),
) -> list[MessageResponse]:
    try:
        session = await auth_service.validate_session(x_session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    try:
        return await service.list_messages(session["user_id"], thread_id)
    except ValueError as exc:
        detail = str(exc)
        if detail == "Thread not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail) from exc
