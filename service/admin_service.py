from fastapi import HTTPException

from models.response_model import UserResponse, AdminUserResponse
from repository.user_repository import UserRepository
from repository.conversation_repository import ConversationRepository
from repository.refresh_token_repository import RefreshTokenRepository

from core.constants import constants


class AdminService:

    def __init__(self, user_repository: UserRepository, conversation_repository: ConversationRepository, refreshtoken_repository: RefreshTokenRepository):
        self.user_repository = user_repository
        self.conversation_repository = conversation_repository
        self.refresh_tkn_repository = refreshtoken_repository

    
    def get_all_users(self):
        users = self.user_repository.get_all_users()
        return [AdminUserResponse(user_id=user[constants.USER_ID], name=user[constants.NAME], email=user[constants.EMAIL], role=user[constants.ROLE], created_at=str(user[constants.CREATED_AT]))for user in users]
    
    
    def get_user(self, user_id: str):
        user = self.user_repository.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=constants.USR_NOT_FOUND)
        return UserResponse(user_id=user[constants.USER_ID], name=user[constants.NAME], email=user[constants.EMAIL], created_at=str(user[constants.CREATED_AT]))
    
    def update_role(self, user_id: str, role: str):
        
        if not self.user_repository.user_exists(user_id):
            raise HTTPException(
                status_code=404,
                detail=constants.USR_NOT_FOUND
            )
        
        if role not in [constants.USER, constants.ADM]:
            raise HTTPException(
                status_code=400,
                detail=constants.INVALID_ROLE
            )
        
        result = self.user_repository.update_role(user_id, role)
        if result[constants.MODIFIED] == 0:
            return {
            constants.MSG: f"User already has the '{role}' role."
        }

        return {
            constants.MSG: constants.USR_ROL_UPDATED,
            constants.USER_ID: user_id,
            constants.ROLE: role
        }
    
    def delete_user(self, user_id: str):
        if not self.user_repository.user_exists(user_id):
            raise HTTPException(status_code=404, detail=constants.USR_NOT_FOUND)
        
        self.refresh_tkn_repository.revoke_all_refresh_tokens(user_id)
        self.conversation_repository.delete_user_threads(user_id)
        self.user_repository.delete_user(user_id)
        return {
            constants.MSG: constants.USR_DEL_SUC
        }
    
    def get_all_conversations(self):
        return self.conversation_repository.get_all_threads()
    
    def delete_conversation(self, thread_id: str):
        if not self.conversation_repository.get_thread(thread_id):
            raise HTTPException(status_code=404, detail=constants.THRD_NOT_FOUND)
        
        self.conversation_repository.delete_thread(thread_id)

        return {
            constants.MSG: constants.CONV_DEL_SUC
        }
