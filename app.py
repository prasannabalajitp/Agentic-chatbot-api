from fastapi import FastAPI
import uvicorn

from routers.users import user_router
from routers.conversations import router as conversation_router
from routers.message import router as message_router
from routers.auth import router as auth_router
from routers.admin import router as admin_router

app = FastAPI(
    title="Chatbot",
    description="Chatbot"
)


app.include_router(admin_router)
app.include_router(user_router)
app.include_router(conversation_router)
app.include_router(message_router)
app.include_router(auth_router)
