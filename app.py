from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers.users import user_router
from routers.conversations import router as conversation_router
from routers.message import router as message_router
from routers.auth import router as auth_router
from routers.admin import router as admin_router
from routers.file import router as file_router
from core.constants import constants
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

app = FastAPI(
    title=constants.CHATBOT,
    description=constants.CHATBOT
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)
app.include_router(user_router)
app.include_router(conversation_router)
app.include_router(message_router)
app.include_router(file_router)
app.include_router(auth_router)
