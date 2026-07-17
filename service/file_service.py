from fastapi import HTTPException

from repository.file_repository import FileRepository
from service.document_parser_service import DocumentParser
from service.embedding_service import EmbeddingService
from models.response_model import CreateFileResponse

from core.constants import constants

class FileService:

    def __init__(self, file_repository: FileRepository, document_service: DocumentParser, embedding_service: EmbeddingService):
        self.file_repository = file_repository
        self.document_service = document_service
        self.embedding_service = embedding_service

    async def create_file_service(self, user_id, thread_id, file):
        raw_text = await self.document_service.extract_text(file)
        create_file_result = self.file_repository.create_file(
            user_id=user_id,
            thread_id=thread_id,
            file_name=file.filename,
            content_type=file.content_type,
            file_size=file.size if hasattr(file, constants.SIZE) else None,
        )

        self.embedding_service.index_document(
            user_id=user_id,
            thread_id=thread_id,
            file_id=(create_file_result[constants.FILE_ID]),
            file_name=file.filename,
            text=raw_text
        )
        return CreateFileResponse(file_id=create_file_result[constants.FILE_ID], thread_id=create_file_result[constants.THREAD_ID], created_at=str(create_file_result[constants.CREATED_AT]), file_name=file.filename)
    
    
    def get_file_service(self, user_id: str, file_id: str):
        file = self.file_repository.get_file(user_id, file_id=file_id)
        if not file:
            raise HTTPException(status_code=404, detail= constants.FILE_NOT_FOUND)
        
        return CreateFileResponse(
            file_id=file[constants.FILE_ID],thread_id=file[constants.THREAD_ID], created_at=str(file[constants.CREATED_AT]),file_name=file[constants.FILE_NAME]
        )

        
    def get_user_files(self, user_id: str):
        user_files = self.file_repository.get_user_files(user_id=user_id)
        if not user_files:
            raise HTTPException(status_code=404, detail=constants.NO_FILES)
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
            raise HTTPException(status_code=404, detail=constants.FILE_NOT_FOUND)
        return {
            constants.MSG: constants.FILE_DEL_SUC
        }
