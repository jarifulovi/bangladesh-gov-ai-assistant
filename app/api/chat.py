from fastapi import APIRouter, Header, HTTPException, status
from bson import ObjectId

from app.core.config import get_settings
from app.models.chat import ChatRequest, ChatResponse
from app.services.auth_service import AuthService
from app.services.history_service import HistoryService
from app.services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()
auth_service = AuthService()
history_service = HistoryService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, x_session_id: str = Header(..., alias="X-Session-Id")) -> ChatResponse:
    settings = get_settings()
    try:
        session = await auth_service.validate_session(x_session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    user_id = session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    thread_id = request.thread_id
    history_messages: list[dict[str, str]] = []
    if thread_id:
        try:
            thread = await history_service.get_thread(user_id, thread_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        thread_obj_id = thread.id
        messages = await history_service.list_messages(user_id, thread_id)
        if settings.max_history_messages > 0:
            history_limit = settings.max_history_messages * 2
            messages = messages[-history_limit:]
        for message in messages:
            history_messages.append({"role": message.role, "content": message.content})
    else:
        thread = await history_service.create_thread(user_id, None)
        thread_obj_id = ObjectId(thread.id)

    await history_service.store_message(
        thread_id=thread_obj_id,
        role="user",
        content=request.message,
    )

    response = await llm_service.generate_response(request, session_id=x_session_id, history=history_messages)

    await history_service.store_message(
        thread_id=thread_obj_id,
        role="assistant",
        content=response.response,
    )
    return ChatResponse(
        response=response.response,
        thread_id=str(thread_obj_id),
    )
