from pydantic import BaseModel, Field
from core.constants import constants

class CreateUserRequest(BaseModel):
    user_id: str = Field(..., description=constants.CRET_USR_DESC)
    name: str | None = None
    email: str | None = None
    password: str | None = None


class CreateConversationRequest(BaseModel):
    title: str = Field(default=constants.DEFAULT_TITLE)


class ChatRequest(BaseModel):
    query: str = Field(..., description=constants.USR_QRY)


class ChatHistoryRequest(BaseModel):
    user_id: str = Field(..., description=constants.USR_IDENTIFIER)
    thread_id: str = Field(..., description=constants.CONV_IDENTIFIER)

class RenameConversatioRequest(BaseModel):
    title: str

class LoginRequest(BaseModel):
    user_id: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class AdminUpdateRole(BaseModel):
    role: str
