from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from core.constants import constants

from core.config import settings

client = MongoClient(settings.MONGODB_URI)
db: Database = client[settings.DATABASE_NAME]

users_collection: Collection = db[constants.USERS]

threads_collection: Collection = db[constants.THREADS]

conversation_collection: Collection = db[constants.CONVERSATIONS]

checkpoints_collection: Collection = db[constants.CHECKPOINTS]

checkpoint_writes_collection: Collection = db[constants.CHECKPOINTS_WRITES]

refresh_tokens_collection: Collection = db[constants.REF_TKN]

file_collection: Collection = db[constants.FILE]

file_vector_collection: Collection = db[constants.FILE_VECTORS]
