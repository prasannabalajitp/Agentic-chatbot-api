from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from database.mongodb import file_vector_collection
from core.config import settings
from core.constants import constants

class EmbeddingService:

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=constants.CHUNK_SIZE,
            chunk_overlap=constants.CHUNK_OVERLAP
        )
        self.embedding_model = NVIDIAEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.NVIDIA_API_KEY)
        

    def index_document(self, user_id: str, thread_id: str, file_id: str, file_name: str, text: str) -> int:
        if not text.strip():
            raise ValueError(constants.INVALID_TXT)
        
        chunks = self.text_splitter.split_text(text)
        if not chunks:
            return 0
        
        try:
            vectors = self.embedding_model.embed_documents(chunks)
        except Exception as e:
            raise RuntimeError(f"{constants.EMB_FAIL} : {e}")

        documents = []
        for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
            documents.append(
                {
                    constants.CHUNK_ID: str(uuid4()),
                    constants.FILE_ID: file_id,
                    constants.THREAD_ID: thread_id,
                    constants.USER_ID: user_id,
                    constants.FILE_NAME: file_name,
                    constants.CHUNK_IDX: index,
                    constants.TXT: chunk,
                    constants.EMBDNG: vector,
                }
            )
        
        file_vector_collection.insert_many(documents)
        return len(documents)
