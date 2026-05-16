"""MongoDB document models."""

from datetime import datetime, UTC
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler: GetCoreSchemaHandler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def validate(cls, value):
        if isinstance(value, ObjectId):
            return value
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)


class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id", exclude=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserDocument(MongoBaseModel):
    email: str = Field(..., min_length=3)
    full_name: Optional[str] = Field(default=None)
    password_hash: str = Field(..., min_length=32)
    password_salt: str = Field(..., min_length=16)


class SessionDocument(MongoBaseModel):
    user_id: PyObjectId
    session_id: str = Field(..., min_length=16)
    expires_at: datetime


class ChatThreadDocument(MongoBaseModel):
    user_id: str = Field(..., min_length=1)
    title: Optional[str] = Field(default=None)


class ChatMessageDocument(MongoBaseModel):
    thread_id: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
