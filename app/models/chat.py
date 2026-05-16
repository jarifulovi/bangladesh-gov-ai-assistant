"""Chat model placeholder."""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    thread_id: Optional[str] = Field(None, description="Optional history thread id")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Model-generated response")
    thread_id: str = Field(..., description="History thread id")
