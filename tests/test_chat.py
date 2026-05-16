"""Chat tests placeholder."""


import os
from datetime import datetime

from bson import ObjectId
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.models.history import ThreadResponse

def test_chat_returns_response(monkeypatch):
    os.environ["BG_ASSISTANT_USE_MOCK"] = "true"
    get_settings.cache_clear()

    async def _validate_session(_session_id: str):
        return {"user_id": ObjectId("507f1f77bcf86cd799439011")}

    async def _create_thread(_user_id: str, _payload):
        return ThreadResponse(id="507f1f77bcf86cd799439011", title=None, created_at=datetime.utcnow())

    async def _list_messages(_user_id: str, _thread_id: str):
        return []

    async def _store_message(**_kwargs):
        return None

    from app.api import chat as chat_api

    monkeypatch.setattr(chat_api.auth_service, "validate_session", _validate_session)
    monkeypatch.setattr(chat_api.history_service, "create_thread", _create_thread)
    monkeypatch.setattr(chat_api.history_service, "list_messages", _list_messages)
    monkeypatch.setattr(chat_api.history_service, "store_message", _store_message)

    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"message": "How do I apply for a passport?"},
        headers={"X-Session-Id": "test-session"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["response"].startswith("Mock response")
    assert payload["thread_id"]
