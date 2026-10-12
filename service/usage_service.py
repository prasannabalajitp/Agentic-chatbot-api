import logging

from repository.usage_repository import UsageRepository

logger = logging.getLogger(__name__)

class UsageService:
    def __init__(self, usage_repository: UsageRepository):
        self.usage_repository = usage_repository

    def get_user_usage(self, user_id):
        logger.info("FETCHING USAGE : %s", user_id)
        return self.usage_repository.get_user_usage(user_id=user_id)
    

    def get_token_usage(self, user_id: str, period: str="7d"):
        logger.info("Fetching token usage | user=%s | period=%s", user_id, period)
        return self.usage_repository.get_token_usage(user_id=user_id, period=period)


    def get_tool_usage(self, user_id: str):
        logger.info("Fetching tool usage | user=%s", user_id)
        return self.usage_repository.get_tool_usage(user_id=user_id)
