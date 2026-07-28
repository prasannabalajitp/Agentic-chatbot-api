from pydantic import BaseModel
from typing import Any


class UserResponse(BaseModel):
    user_id: str
    name: str | None = None
    email: str | None = None
    created_at: str | None = None

class AdminUserResponse(BaseModel):
    user_id: str
    name: str | None = None
    email: str | None = None
    role: str | None = None
    created_at: str | None = None

class CreateConversationResponse(BaseModel):
    thread_id: str
    user_id: str
    title: str
    created_at: str


class ChatResponse(BaseModel):
    response: str


class MessageResponse(BaseModel):
    message: str


class ChatHistoryResponse(BaseModel):
    history: list[Any]

class ConversationResponse(BaseModel):
    thread_id: str
    user_id: str
    title: str
    message_count: int
    created_at: str
    updated_at: str

class ConversationListResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_previous: bool
    has_next: bool
    conversations: list[ConversationResponse]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class CreateFileResponse(BaseModel):
    file_id: str
    thread_id: str
    created_at: str
    file_name: str
