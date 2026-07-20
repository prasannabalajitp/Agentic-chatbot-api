from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from core.config import settings
from database.mongodb import file_vector_collection

class RetrievalService:

    def __init__(self):
        self.embedding_model = NVIDIAEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.NVIDIA_API_KEY
        )

    def retrieve(self, query: str, user_id: str, thread_id: str, limit: int = 5):
        query_vector = self.embedding_model.embed_query(query)

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
                    "score": {
                        "$meta": "vectorSearchScore"
                    }
                }
            }
        ]

        results = list(file_vector_collection.aggregate(pipeline))
        return [
            {
                "file_name": result["file_name"],
                "chunk_index": result["chunk_index"],
                "text": result["text"],
                "score": round(result["score"], 2)
            }
            for result in results
        ]
