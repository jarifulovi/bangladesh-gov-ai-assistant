
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.history import router as history_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(history_router, tags=["history"])
api_router.include_router(chat_router, prefix="", tags=["chat"])
