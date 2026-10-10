from repository.user_repository import UserRepository
from repository.conversation_repository import ConversationRepository
from repository.refresh_token_repository import RefreshTokenRepository

from models.response_model import UserResponse, TokenResponse
from core.constants import constants
from core.security import hash_password, verify_password, create_access_token, create_refresh_token, hash_refresh_token, verify_refresh_token

from exceptions.application import ResourceNotFoundError, ResourceConflictError, ValidationError, AuthenticationError

from datetime import datetime, timezone
import math

class UserService:

    def __init__(self, user_repository: UserRepository, conversation_repository: ConversationRepository, refreshtoken_repository: RefreshTokenRepository):
        self.user_repository = user_repository
        self.conversation_repository = conversation_repository
        self.refresh_token_repository = refreshtoken_repository
    
    def create_user(self, user_id: str, password: str, name: str | None = None, email: str | None = None):
        if self.user_repository.user_exists(user_id):
            raise ResourceConflictError(
                constants.USR_EXISTS,
                code=constants.USR_EXISTS
            )
        
        password_hash = hash_password(password)
        
        create_result = self.user_repository.create_user(
            user_id=user_id,
            password_hash=password_hash,
            name=name,
            email=email,
            role=constants.USER
        )

        data = UserResponse(
                user_id=create_result[constants.USER_ID], 
                name=create_result[constants.NAME], 
                email=create_result[constants.EMAIL], 
                created_at=str(create_result[constants.CREATED_AT])
            )
        return data
    
    def login(self, user_id: str, password: str):

        user = self.user_repository.get_user(user_id)

        if not user or not verify_password(password, user[constants.HASHED_PWD]):
            raise AuthenticationError(
                constants.INVALID_UNAME_PWD,
                code="INVALID_CREDENTIALS",
            )
        
        access_token = create_access_token({
            constants.SUB: user[constants.USER_ID],
            constants.ROLE: user[constants.ROLE]
        })

        refresh_token, exp = create_refresh_token({constants.SUB: user_id})
        token_hash = hash_refresh_token(refresh_token)

        self.refresh_token_repository.save_refresh_token(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=exp
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    
    def get_user(self, user_id: str):
        user = self.user_repository.get_user(user_id)

        if not user:
            raise ResourceNotFoundError(
                constants.USR_NOT_FOUND,
                code=constants.USR_NOT_FOUND,
            )
        
        user = UserResponse(user_id=user[constants.USER_ID], name=user[constants.NAME], email=user[constants.EMAIL], created_at=str(user[constants.CREATED_AT]))
        return user
    
    def get_all_users(self):
        return self.user_repository.get_all_users()
    

    def get_user_conversation(self, user_id: str, page: int=1, limit: int=20):
        if page < 1:
            raise ValidationError(
                constants.PAGE_EXCP,
                code="INVALID_PAGE",
            )
        if limit < 1 or limit > 100:
            raise ValidationError(
                constants.LMT_EXCP,
                code="INVALID_LIMIT",
            )
        
        if not self.user_repository.user_exists(user_id=user_id):
            raise ResourceNotFoundError(
                constants.USR_NOT_FOUND,
                code="USER_NOT_FOUND",
            )
        
        skip = (page - 1) * limit
        conversations, total = self.conversation_repository.get_user_threads(user_id=user_id, skip=skip, limit=limit)

        return {
            constants.PAGE: page,
            constants.LIMIT: limit,
            constants.TOTAL: total,
            constants.TTL_PAGES: math.ceil(total / limit),
            constants.HAS_PREV: page > 1,
            constants.HAS_NXT: skip + limit < total,
            constants.ITEMS: [
                {
                    constants.THREAD_ID: conversation[constants.THREAD_ID],
                    constants.USER_ID: conversation[constants.USER_ID],
                    constants.TITLE: conversation[constants.TITLE],
                    constants.MSG_COUNT: conversation.get(constants.MSG_COUNT, 0),
                    constants.CREATED_AT: str(conversation[constants.CREATED_AT]),
                    constants.UPDATED_AT: str(conversation[constants.UPDATED_AT])
                }
                for conversation in conversations
            ]
        }
    
    def delete_user(self, user_id: str):

        if not self.user_repository.user_exists(user_id):
            raise ResourceNotFoundError(
                constants.USR_NOT_FOUND,
                code=constants.USR_NOT_FOUND,
            )
        
        self.user_repository.delete_user(user_id)
        return {
            constants.MSG: constants.USR_DEL_SUC
        }

    def _verify_refresh_token(self, refresh_token: str) -> dict:
        try:
            return verify_refresh_token(refresh_token)

        except AuthenticationError:
            raise

        except Exception as exc:
            raise AuthenticationError(
                constants.INVALID_TKN,
                code="INVALID_REFRESH_TOKEN",
            ) from exc
    
    def refresh(self, refresh_token: str):
        payload = self._verify_refresh_token(refresh_token)
        user_id = payload.get(constants.SUB)
        
        if not user_id:
            raise AuthenticationError(
                constants.INVALID_TKN,
                code="INVALID_REFRESH_TOKEN",
            )
        
        token_hash = hash_refresh_token(refresh_token)
        user = self.user_repository.get_user(user_id)
        token = self.refresh_token_repository.get_refresh_token(token_hash)

        if not user or not token:
            raise AuthenticationError(
                constants.INVALID_TKN,
                code="INVALID_REFRESH_TOKEN",
            )
        
        expires_at = token.get(constants.EXP_AT)

        if expires_at is not None:
            if expires_at.tzinfo is not None:
                expires_at = expires_at.astimezone(timezone.utc).replace(
                    tzinfo=None
                )

            now = datetime.now(timezone.utc).replace(tzinfo=None)

            if expires_at <= now:
                raise AuthenticationError(
                    constants.INVALID_TKN,
                    code="INVALID_REFRESH_TOKEN",
                )
        
        access_token = create_access_token({
            constants.SUB: user_id,
            constants.ROLE: user[constants.ROLE]
        })

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    
    def logout(self, refresh_token: str):
        payload = self._verify_refresh_token(refresh_token)

        if not payload.get(constants.SUB):
            raise AuthenticationError(
                constants.INVALID_TKN,
                code="INVALID_REFRESH_TOKEN",
            )

        token_hash = hash_refresh_token(refresh_token)
        token = self.refresh_token_repository.get_refresh_token(token_hash)

        if not token:
            raise AuthenticationError(
                constants.INVALID_TKN,
                code="INVALID_REFRESH_TOKEN",
            )

        self.refresh_token_repository.revoke_refresh_token(token_hash)

        return {
            constants.MSG: constants.LOG_OUT_SUC,
        }
    
    def logout_all(self, current_user: dict):
        user_id = current_user.get(constants.USER_ID)
        if not user_id:
            raise AuthenticationError(
                "Authenticated user information is missing.",
                code="INVALID_USER_CONTEXT",
            )
        self.refresh_token_repository.revoke_all_refresh_tokens(user_id)
        return {
            constants.MSG: constants.LOG_OUT_ALL,
        }
