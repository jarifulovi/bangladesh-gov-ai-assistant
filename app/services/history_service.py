"""Chat history service for threads and messages."""

from __future__ import annotations

import secrets

from bson import ObjectId

from app.db.database import get_chat_collection, get_threads_collection
from app.db.models import ChatMessageDocument, ChatThreadDocument
from app.models.history import MessageResponse, ThreadCreateRequest, ThreadRenameRequest, ThreadResponse


class HistoryService:
    async def create_thread(self, user_id: str, payload: ThreadCreateRequest | None = None) -> ThreadResponse:
        threads = get_threads_collection()
        title = payload.title if payload and payload.title else f"New Thread-{secrets.randbelow(10000):04d}"
        thread_doc = ChatThreadDocument(user_id=user_id, title=title)
        result = await threads.insert_one(thread_doc.model_dump(by_alias=True))
        return ThreadResponse(id=str(result.inserted_id), title=thread_doc.title, created_at=thread_doc.created_at)

    async def get_thread(self, user_id: str, thread_id: str) -> ChatThreadDocument:
        threads = get_threads_collection()
        try:
            obj_id = ObjectId(thread_id)
        except Exception as exc:
            raise ValueError("Invalid thread id") from exc
        thread = await threads.find_one({"_id": obj_id, "user_id": user_id})
        print("SESSION USER:", user_id)
        print("THREAD FOUND:", thread)
        if not thread:
            raise ValueError("Thread not found")
        return ChatThreadDocument.model_validate(thread)

    async def rename_thread(self, user_id: str, thread_id: str, payload: ThreadRenameRequest) -> ThreadResponse:
        thread = await self.get_thread(user_id, thread_id)
        threads = get_threads_collection()
        await threads.update_one({"_id": thread.id}, {"$set": {"title": payload.title}})
        return ThreadResponse(id=str(thread.id), title=payload.title, created_at=thread.created_at)

    async def list_threads(self, user_id: str) -> list[ThreadResponse]:
        threads = get_threads_collection()
        results: list[ThreadResponse] = []
        async for doc in threads.find({"user_id": user_id}).sort("created_at", -1):
            results.append(
                ThreadResponse(
                    id=str(doc["_id"]),
                    title=doc.get("title"),
                    created_at=doc.get("created_at"),
                )
            )
        return results

    async def list_messages(self, user_id: str, thread_id: str) -> list[MessageResponse]:
        thread = await self.get_thread(user_id, thread_id)
        messages = get_chat_collection()
        results: list[MessageResponse] = []
        async for doc in messages.find({"thread_id": str(thread.id)}).sort("created_at", 1):
            results.append(
                MessageResponse(
                    id=str(doc["_id"]),
                    role=doc.get("role"),
                    content=doc.get("content"),
                    created_at=doc.get("created_at"),
                )
            )
        return results

    async def store_message(
        self,
        thread_id: ObjectId | str,
        role: str,
        content: str,
    ) -> None:
        messages = get_chat_collection()
        thread_id_value = str(thread_id)
        message_doc = ChatMessageDocument(
            thread_id=thread_id_value,
            role=role,
            content=content,
        )
        await messages.insert_one(message_doc.model_dump(by_alias=True))
