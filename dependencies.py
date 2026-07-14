from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials

from jose import JWTError

from common.chatbot_graph import graph
from core.security import verify_access_token
from llm.nvidia_llm import llm, chat_model

from repository.conversation_repository import ConversationRepository
from repository.user_repository import UserRepository

from service.conversation_service import ConversationService
from service.user_service import UserService
from service.weather_service import WeatherService
from service.web_search_service import WebSearchService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)
security = HTTPBearer()

user_repository = UserRepository()
conversation_repository = ConversationRepository()

weather_service = WeatherService()
websearch_service = WebSearchService()

user_service = UserService(user_repository=user_repository, conversation_repository=conversation_repository)

conversation_service = ConversationService(user_repository, conversation_repository, graph, llm)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = verify_access_token(token)

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        
        user = user_repository.get_user(user_id)

        if not user:
            raise HTTPException(status_code=401, detail="User Not Found")
        return user
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
