from uuid import uuid4

from langchain_core.documents import Document
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import settings
from core.constants import constants
from database.mongodb import file_vector_collection


class EmbeddingService:

    def __init__(self):

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=constants.CHUNK_SIZE,
            chunk_overlap=constants.CHUNK_OVERLAP,
        )

        self.embedding_model = NVIDIAEmbeddings(model=settings.EMBEDDING_MODEL, api_key=settings.NVIDIA_API_KEY)

    def index_document(self, user_id: str, thread_id: str, file_id: str, file_name: str, documents: list[Document]) -> int:
        """
        Split LangChain Documents, generate embeddings,
        and store them in MongoDB.
        """
        if not documents:
            raise ValueError(constants.INVALID_TXT)

        chunks = self.text_splitter.split_documents(documents)

        if not chunks:
            return 0

        try:
            vectors = []
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

        except Exception as e:
            raise RuntimeError(f"{constants.EMB_FAIL}: {e}") from e

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
            file_vector_collection.insert_many(mongo_documents)

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
        except Exception as e:
            return str(e)
