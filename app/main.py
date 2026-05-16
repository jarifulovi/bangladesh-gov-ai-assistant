from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError
from fastapi import status

from app.api.router import api_router
from app.core.config import get_settings
from app.core.model_loader import get_model_loader
from app.db.database import ping_database

load_dotenv()

class SessionHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/chat":
            session_id = request.headers.get("X-Session-Id")
            if not session_id:
                return JSONResponse(
                    {"detail": "Missing X-Session-Id header"},
                    status_code=401,
                )
        return await call_next(request)


app = FastAPI(title="Bangladesh Government Services Chatbot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionHeaderMiddleware)


@app.on_event("startup")
async def preload_model() -> None:
    settings = get_settings()
    if settings.use_mock:
        return
    get_model_loader().load()


@app.get("/health")
async def health_check():
    db_ok = await ping_database()
    return {"status": "ok", "db": "ok" if db_ok else "unavailable"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print("[DEBUG] Validation error:", exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

app.include_router(api_router)
