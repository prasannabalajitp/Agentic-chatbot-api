from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from core.config import settings
from core.constants import constants
from database.mongodb import file_vector_collection
from exceptions.database import DatabaseError, DatabaseOperationError, DatabaseConnectionError
from exceptions.external_service import ExternalServiceError

from numbers import Real
from time import perf_counter

class RetrievalService:

    DEFAULT_LIMIT = 5
    DEFAULT_NUM_CANDIDATES = 100

    def __init__(self):
        self.embedding_model = NVIDIAEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.NVIDIA_API_KEY
        )

    @staticmethod
    def _validate_search_parameters(limit: int, num_candidates: int) -> None:
        if limit < 1:
            raise ValueError(constants.LIMIT_VALIDATION)

        if num_candidates < limit:
            raise ValueError(constants.NUM_CAND_VALIDATION)


    @staticmethod
    def _raise_database_error(exc: Exception) -> None:
        if isinstance(exc, DatabaseError):
            raise exc

        if isinstance(exc, (ConnectionFailure, ServerSelectionTimeoutError)):
            raise DatabaseConnectionError() from exc

        raise DatabaseOperationError() from exc


    @staticmethod
    def _map_result(result: dict) -> dict | None:
        text = result.get(constants.TXT)
        file_name = result.get(constants.FILE_NAME)
        chunk_index = result.get(constants.CHUNK_IDX)
        score = result.get("score")

        if not isinstance(text, str) or not text.strip():
            return None

        if not isinstance(file_name, str) or not file_name.strip():
            return None

        if not isinstance(chunk_index, int) or isinstance(chunk_index, bool):
            return None

        if (not isinstance(score, Real) or isinstance(score, bool)):
            return None

        return {
            "file_name": file_name,
            "chunk_index": chunk_index,
            "text": text,
            "metadata": result.get(constants.METADATA, {}),
            "score": round(float(score), 4),
        }

    def retrieve(self, query: str, user_id: str, thread_id: str, limit: int = DEFAULT_LIMIT, num_candidates: int = DEFAULT_NUM_CANDIDATES):

        search_started = perf_counter()

        if not isinstance(query, str) or not query.strip():
            raise ValueError(constants.QUERY_VALIDATION)

        if not user_id or not thread_id:
            raise ValueError(constants.USR_ID_VALIDATION)

        self._validate_search_parameters(limit, num_candidates)
        try:
            query_vector = self.embedding_model.embed_query(query)

        except Exception as e:
            raise ExternalServiceError(constants.EMBEDDING_ERR) from e

        pipeline = [
            {
                "$vectorSearch": {
                    "index": "file_vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": num_candidates,
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
            search_duration_ms = round((perf_counter() - search_started) * 1000, 2)

        except DatabaseError:
            raise

        except Exception as exc:
            self._raise_database_error(exc)

        except Exception as e:
            if isinstance(e, (ConnectionFailure, ServerSelectionTimeoutError),):
                raise DatabaseConnectionError() from e

            raise DatabaseOperationError() from e

        documents = []
        
        for result in results:
            document = self._map_result(result)
            if document is None:
                print(constants.VECTOR_VALIDATION)
                continue

            documents.append(document)
        return documents
