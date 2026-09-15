from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials

from core.constants import constants
from core.security import verify_access_token
from llm.nvidia_llm import llm, title_llm
from common.deepagent import deep_agent

from repository.conversation_repository import ConversationRepository
from repository.user_repository import UserRepository
from repository.refresh_token_repository import RefreshTokenRepository
from repository.file_repository import FileRepository

from service.agent_service import AgentService
from service.conversation_service import ConversationService
from service.user_service import UserService
from service.web_search_service import WebSearchService
from service.admin_service import AdminService
from service.file_service import FileService
from service.document_parser_service import DocumentParser
from service.embedding_service import EmbeddingService
from service.retrieval_service import RetrievalService
from service.guardrail_service import GuardRailService
from service.title_service import TitleService
from service.chat_service import ChatService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)
security = HTTPBearer()

user_repository = UserRepository()
conversation_repository = ConversationRepository()
refresh_tkn_repository = RefreshTokenRepository()
file_repository = FileRepository()

websearch_service = WebSearchService()
document_service = DocumentParser()
embedding_service = EmbeddingService()
retrieval_service = RetrievalService()
agent_service = AgentService(deepagent=deep_agent)
guardrail_service = GuardRailService(llm)
title_service = TitleService(title_llm=title_llm, user_repository=user_repository, conversation_repository=conversation_repository)
chat_service = ChatService(agent_service=agent_service, conversation_repository=conversation_repository, guardrail_service=guardrail_service, title_service=title_service, file_repository=file_repository)
file_service = FileService(file_repository=file_repository,document_service=document_service, embedding_service=embedding_service)


user_service = UserService(user_repository=user_repository, conversation_repository=conversation_repository, refreshtoken_repository=refresh_tkn_repository)

conversation_service = ConversationService(user_repository, conversation_repository, deep_agent, llm, title_llm, guardrail_service, title_service)

admin_service = AdminService(user_repository, conversation_repository, refresh_tkn_repository)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_access_token(token)

    user_id = payload.get(constants.SUB)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail=constants.INVALID_TKN
        )
    
    user = user_repository.get_user(user_id)

    if not user:
        raise HTTPException(status_code=401, detail=constants.USR_NOT_FOUND)
    return user
    
def require_roles(*allowed_roles):
    def role_checker(current_user: dict = Depends(get_current_user)):

        if current_user[constants.ROLE] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=constants.FORBIDDEN
            )

        return current_user

    return role_checker
