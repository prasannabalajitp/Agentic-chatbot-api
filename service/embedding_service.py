# from uuid import uuid4

# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

# from database.mongodb import file_vector_collection
# from core.config import settings
# from core.constants import constants

# class EmbeddingService:

#     def __init__(self):
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=constants.CHUNK_SIZE,
#             chunk_overlap=constants.CHUNK_OVERLAP
#         )
#         self.embedding_model = NVIDIAEmbeddings(
#             model=settings.EMBEDDING_MODEL,
#             api_key=settings.NVIDIA_API_KEY)
        

#     def index_document(self, user_id: str, thread_id: str, file_id: str, file_name: str, text: str) -> int:
#         if not text.strip():
#             raise ValueError(constants.INVALID_TXT)
        
#         chunks = self.text_splitter.split_text(text)
#         if not chunks:
#             return 0
        
#         try:
#             vectors = []

#             BATCH_SIZE = 8

#             for i in range(0, len(chunks), BATCH_SIZE):
#                 batch = chunks[i:i + BATCH_SIZE]

#                 batch_vectors = self.embedding_model.embed_documents(batch)

#                 vectors.extend(batch_vectors)

#         except Exception as e:
#             raise RuntimeError(f"{constants.EMB_FAIL} : {e}") from e

#         documents = []
#         for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
#             documents.append(
#                 {
#                     constants.CHUNK_ID: str(uuid4()),
#                     constants.FILE_ID: file_id,
#                     constants.THREAD_ID: thread_id,
#                     constants.USER_ID: user_id,
#                     constants.FILE_NAME: file_name,
#                     constants.CHUNK_IDX: index,
#                     constants.TXT: chunk,
#                     constants.EMBDNG: vector,
#                 }
#             )
        
#         file_vector_collection.insert_many(documents)
#         return len(documents)
    
#     def delete_embeddings(self, file_id: str):
#         try:
#             result = file_vector_collection.delete_many({
#                 constants.FILE_ID: file_id
#             })
#             return result.deleted_count
        
#         except Exception as e:
#             return str(e)


from uuid import uuid4
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from langchain_core.documents import Document
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import settings
from core.constants import constants
from database.mongodb import file_vector_collection
from exceptions.database import DatabaseError, DatabaseConnectionError, DatabaseOperationError
from exceptions.application import ValidationError
from exceptions.external_service import ExternalServiceError


class EmbeddingService:

    def __init__(self):

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=constants.CHUNK_SIZE,
            chunk_overlap=constants.CHUNK_OVERLAP,
        )

        self.embedding_model = NVIDIAEmbeddings(model=settings.EMBEDDING_MODEL, api_key=settings.NVIDIA_API_KEY)


    @staticmethod
    def _raise_database_error(exc: Exception) -> None:
        if isinstance(exc, DatabaseError):
            raise exc

        if isinstance(exc, (ConnectionFailure, ServerSelectionTimeoutError)):
            raise DatabaseConnectionError() from exc
        
        raise DatabaseOperationError() from exc

    def index_document(self, user_id: str, thread_id: str, file_id: str, file_name: str, documents: list[Document]) -> int:
        """
        Split LangChain Documents, generate embeddings,
        and store them in MongoDB.
        """
        if not documents:
            raise ValidationError(
                constants.INVALID_TXT,
                code="INVALID_DOCUMENT_CONTENT"
            )

        chunks = self.text_splitter.split_documents(documents)

        if not chunks:
            return 0

        vectors = []
        try:
            batch_size = 8
            for start in range(0, len(chunks), batch_size,):
                batch = chunks[start:start + batch_size]

                batch_vectors = (
                    self.embedding_model.embed_documents(
                        [
                            document.page_content
                            for document in batch
                        ]
                    )
                )

                vectors.extend(batch_vectors)

        except Exception as exc:
            raise ExternalServiceError("Unable to generate document embeddings.") from exc

        if len(vectors) != len(chunks):
            raise ExternalServiceError("Embedding generation returned an unexpected result.")

        mongo_documents = []
        for index, (chunk, vector) in enumerate(zip(chunks, vectors)):

            metadata = chunk.metadata.copy()
            metadata[constants.CHUNK_IDX] = index

            mongo_documents.append(
                {
                    constants.CHUNK_ID: str(uuid4()),
                    constants.FILE_ID: file_id,
                    constants.THREAD_ID: thread_id,
                    constants.USER_ID: user_id,
                    constants.FILE_NAME: file_name,
                    constants.CHUNK_IDX: index,
                    constants.TXT: chunk.page_content,
                    constants.EMBDNG: vector,
                    constants.METADATA: metadata,
                }
            )

        if mongo_documents:
            try:
                file_vector_collection.insert_many(mongo_documents)
            except DatabaseError:
                raise
            except Exception as exc:
                self._raise_database_error(exc)

        return len(mongo_documents)

    def delete_embeddings(self, file_id: str):
        """
        Delete all embeddings associated with a file.
        """
        try:
            result = file_vector_collection.delete_many(
                {
                    constants.FILE_ID: file_id
                }
            )
            return result.deleted_count
        
        except DatabaseError:
            raise

        except Exception as exc:
            self._raise_database_error(exc)
