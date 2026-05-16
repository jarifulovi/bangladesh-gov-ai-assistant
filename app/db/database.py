"""MongoDB connection setup."""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncIOMotorClient(settings.mongodb_url)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    settings = get_settings()
    return get_client()[settings.mongodb_db]


async def ping_database() -> bool:
    db = get_database()
    result = await db.command("ping")
    return bool(result.get("ok"))


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_users_collection():
    return get_database()["users"]


def get_sessions_collection():
    return get_database()["sessions"]


def get_chat_collection():
    return get_database()["chat_messages"]


def get_threads_collection():
    return get_database()["chat_threads"]
