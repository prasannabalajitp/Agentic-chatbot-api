from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver

from core.config import settings

client = MongoClient(settings.MONGODB_URI)

checkpointer = MongoDBSaver(
    client=client,
    db_name=settings.DATABASE_NAME
)
