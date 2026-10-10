from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from core.config import settings
from database.mongodb import file_vector_collection
from exceptions.database import DatabaseError, DatabaseOperationError, DatabaseConnectionError
from exceptions.external_service import ExternalServiceError

class RetrievalService:

    def __init__(self):
        self.embedding_model = NVIDIAEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.NVIDIA_API_KEY
        )

    def retrieve(self, query: str, user_id: str, thread_id: str, limit: int = 3):
        try:
            query_vector = self.embedding_model.embed_query(query)

        except Exception as e:
            raise ExternalServiceError("Unable to generate the query emebeddings") from e

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "file_vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": limit,
                    "filter": {
                        "user_id": user_id,
                        "thread_id": thread_id
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "file_name": 1,
                    "chunk_index": 1,
                    "text": 1,
                    "metadata": 1,
                    "score": {
                        "$meta": "vectorSearchScore"
                    }
                }
            }
        ]

        try:
            results = list(file_vector_collection.aggregate(pipeline))

        except DatabaseError:
            raise

        except Exception as e:
            if isinstance(e, (ConnectionFailure, ServerSelectionTimeoutError),):
                raise DatabaseConnectionError() from e

            raise DatabaseOperationError() from e
        return [
            {
                "file_name": result["file_name"],
                "chunk_index": result["chunk_index"],
                "text": result["text"],
                "metadata": result.get("metadata", {}),
                "score": round(result["score"], 2)
            }
            for result in results
        ]
