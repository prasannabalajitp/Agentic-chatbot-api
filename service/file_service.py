from repository.file_repository import FileRepository
from service.document_parser_service import DocumentParser
from service.embedding_service import EmbeddingService
from models.response_model import CreateFileResponse

from core.constants import constants
from exceptions.application import ResourceNotFoundError

class FileService:

    def __init__(self, file_repository: FileRepository, document_service: DocumentParser, embedding_service: EmbeddingService):
        self.file_repository = file_repository
        self.document_service = document_service
        self.embedding_service = embedding_service

    async def create_file_service(self, user_id, thread_id, file):
        # raw_text = await self.document_service.extract_text(file)
        
        file_record = None
        try: 
            documents = await self.document_service.extract_documents(file)

            if isinstance(documents, Exception):
                raise documents
            
            file_record = self.file_repository.create_file(
                user_id=user_id,
                thread_id=thread_id,
                file_name=file.filename,
                content_type=file.content_type,
                file_size=(
                    file.size
                    if hasattr(file, constants.SIZE)
                    else None
                ),
            )

            file_id = file_record[constants.FILE_ID]

            self.embedding_service.index_document(
                user_id=user_id,
                thread_id=thread_id,
                file_id=file_id,
                file_name=file.filename,
                documents=documents,
            )

            return CreateFileResponse(
                file_id=file_id,
                thread_id=file_record[constants.THREAD_ID],
                created_at=str(file_record[constants.CREATED_AT]),
                file_name=file.filename,
            )

        except Exception:
            if file_record:
                file_id = file_record.get(constants.FILE_ID)

                if file_id:
                    try:
                        self.embedding_service.delete_embeddings(file_id)
                        self.file_repository.delete_file(
                            user_id=user_id,
                            file_id=file_id,
                        )
                    except Exception:
                        raise
            raise
    
    
    def get_file_service(self, user_id: str, file_id: str):
        file = self.file_repository.get_file(user_id, file_id=file_id)
        if not file:
            raise ResourceNotFoundError(
                constants.FILE_NOT_FOUND,
                code=constants.FILE_NOT_FOUND
            )
        
        return CreateFileResponse(
            file_id=file[constants.FILE_ID],thread_id=file[constants.THREAD_ID], created_at=str(file[constants.CREATED_AT]),file_name=file[constants.FILE_NAME]
        )

        
    def get_user_files(self, user_id: str):
        user_files = self.file_repository.get_user_files(user_id=user_id)
        if not user_files:
            raise ResourceNotFoundError(
                constants.NO_FILES,
                code=constants.NO_FILES
            )
        return [
                CreateFileResponse(
                    file_id=file_doc[constants.FILE_ID], 
                    thread_id=file_doc[constants.THREAD_ID], 
                    created_at=str(file_doc[constants.CREATED_AT]), 
                    file_name=file_doc[constants.FILE_NAME],
                ) 
                for file_doc in user_files
            ]
    
    def delete_file_service(self, user_id: str, file_id: str):
        result = self.file_repository.delete_file(
            user_id=user_id,
            file_id=file_id
        )
        if result.deleted_count == 0:
            raise ResourceNotFoundError(
                constants.FILE_NOT_FOUND,
                code=constants.FILE_NOT_FOUND
            )
        
        self.embedding_service.delete_embeddings(file_id)
        return {
            constants.MSG: constants.FILE_DEL_SUC
        }

    def get_thread_files(self, user_id: str, thread_id: str):
        thread_files = self.file_repository.get_thread_files(user_id, thread_id)
        if not thread_files:
            raise ResourceNotFoundError(
                constants.NO_FILES,
                code=constants.NO_FILES
            )
        return [
                CreateFileResponse(
                    file_id=file_doc[constants.FILE_ID], 
                    thread_id=file_doc[constants.THREAD_ID], 
                    created_at=str(file_doc[constants.CREATED_AT]), 
                    file_name=file_doc[constants.FILE_NAME],
                ) 
                for file_doc in thread_files
            ]
