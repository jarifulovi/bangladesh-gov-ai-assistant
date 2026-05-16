"""Simple session-based authentication service."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, UTC

from bson import ObjectId

from app.db.database import get_sessions_collection, get_users_collection
from app.db.models import UserDocument
from app.models.auth import AuthMeResponse, AuthResponse, LoginRequest, RegisterRequest

_SESSION_TTL_DAYS = 7


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


class AuthService:
    async def register(self, payload: RegisterRequest) -> AuthResponse:
        users = get_users_collection()
        existing = await users.find_one({"email": payload.email})
        if existing:
            raise ValueError("Email already registered")

        salt = secrets.token_hex(16)
        password_hash = _hash_password(payload.password, salt)
        user_doc = UserDocument(
            email=payload.email,
            full_name=payload.full_name,
            password_hash=password_hash,
            password_salt=salt,
        )
        result = await users.insert_one(user_doc.model_dump(by_alias=True, exclude_none=True))
        print("[DEBUG] Inserted user_id:", result.inserted_id)
        if not result.inserted_id:
            raise ValueError("Failed to create user: no user_id returned from DB")
        return await self._create_session(result.inserted_id)

    async def login(self, payload: LoginRequest) -> AuthResponse:
        users = get_users_collection()
        user = await users.find_one({"email": payload.email})
        if not user:
            raise ValueError("Invalid credentials")

        salt = user.get("password_salt")
        expected = user.get("password_hash")
        if not salt or not expected:
            raise ValueError("Invalid credentials")

        if _hash_password(payload.password, salt) != expected:
            raise ValueError("Invalid credentials")

        user_id = user.get("_id")
        if not user_id:
            raise ValueError("User ID missing in database record")
        return await self._create_session(user_id)

    async def _create_session(self, user_id: ObjectId | str) -> AuthResponse:
        if not user_id:
            raise ValueError("User ID is required for session creation")
        user_id_value = str(user_id)
        sessions = get_sessions_collection()
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(days=_SESSION_TTL_DAYS)
        session_doc = {
            "user_id": user_id_value,
            "session_id": session_id,
            "expires_at": expires_at,
            "created_at": datetime.now(UTC),
        }
        await sessions.insert_one(session_doc)
        return AuthResponse(user_id=user_id_value, session_id=session_id)

    async def me(self, session_id: str) -> AuthMeResponse:
        session = await self._get_valid_session(session_id)
        users = get_users_collection()
        user_id_value = session["user_id"]
        if isinstance(user_id_value, str) and ObjectId.is_valid(user_id_value):
            user_id_value = ObjectId(user_id_value)
        user = await users.find_one({"_id": user_id_value})
        if not user:
            raise ValueError("User not found")

        return AuthMeResponse(
            user_id=str(user["_id"]),
            email=user["email"],
            full_name=user.get("full_name"),
            session_id=session_id,
        )

    async def logout(self, session_id: str) -> None:
        sessions = get_sessions_collection()
        await sessions.delete_one({"session_id": session_id})

    async def _get_valid_session(self, session_id: str):
        sessions = get_sessions_collection()
        session = await sessions.find_one({"session_id": session_id})
        if not session:
            raise ValueError("Invalid session")

        expires_at = session.get("expires_at")
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at and expires_at < datetime.now(UTC):
            await sessions.delete_one({"_id": session["_id"]})
            raise ValueError("Session expired")

        return session

    async def validate_session(self, session_id: str):
        return await self._get_valid_session(session_id)
