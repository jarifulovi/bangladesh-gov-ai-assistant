"""History schemas for threads and messages."""

from datetime import datetime

from pydantic import BaseModel, Field


class ThreadCreateRequest(BaseModel):
    title: str | None = Field(default=None, description="Optional thread title")


class ThreadRenameRequest(BaseModel):
    title: str = Field(..., min_length=1, description="New thread title")


class ThreadResponse(BaseModel):
    id: str = Field(..., description="Thread id")
    title: str | None = None
    created_at: datetime


class MessageResponse(BaseModel):
    id: str = Field(..., description="Message id")
    role: str
    content: str
    created_at: datetime
