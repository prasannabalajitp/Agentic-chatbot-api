from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import HumanMessage
from core.constants import constants

class RetryEmptyResponseMiddleware(AgentMiddleware):

    def __init__(self, max_retries: int = 1):
        super().__init__()
        self.max_retries = max_retries

    def _is_valid_response(self, response) -> bool:
        result = getattr(response, constants.RESULT, None)
        message = result[0] if result else response

        if getattr(message, constants.TOOL_CALLS, None):
            return True

        content = getattr(message, constants.CONTENT, None)

        if isinstance(content, str):
            return bool(content.strip())

        if isinstance(content, list):
            return any(
                isinstance(item, dict)
                and item.get(constants.TYPE) == constants.TXT
                and item.get(constants.TXT, constants.EMPTY_STRING).strip()
                for item in content
            )

        return bool(content)

    def _retry_request(self, request, attempt):
        if attempt == 0:
            return request

        messages = list(request.messages)

        messages.append(
            HumanMessage(
                content=constants.RETRY_CNTNT
            )
        )

        return request.override(messages=messages)

    def wrap_model_call(self, request, handler):
        response = None

        for attempt in range(self.max_retries + 1):
            retry_request = self._retry_request(request, attempt)
            response = handler(retry_request)

            if self._is_valid_response(response):
                return response

        return response

    async def awrap_model_call(self, request, handler):
        response = None

        for attempt in range(self.max_retries + 1):
            retry_request = self._retry_request(request, attempt)
            response = await handler(retry_request)

            if self._is_valid_response(response):
                return response

        return response
