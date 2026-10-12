from langchain.agents.middleware import AgentMiddleware

from core.constants import constants
from exceptions.tool import ToolDisabledError, ToolNotRegisteredError
from tools.tool_registry import registry


class ToolPolicyMiddleware(AgentMiddleware):
    def _validate_tool(self, tool_name: str) -> None:
        metadata = registry.get_metadata(tool_name)

        if metadata is None:
            raise ToolNotRegisteredError(f"Tool '{tool_name}' is not registered.")

        if not metadata.enabled:
            raise ToolDisabledError(f"Tool '{tool_name}' is disabled.")

    def wrap_tool_call(self, request, handler):
        tool_name = request.tool_call[constants.NAME]
        self._validate_tool(tool_name)
        return handler(request)

    async def awrap_tool_call(self, request, handler):
        tool_name = request.tool_call[constants.NAME]
        self._validate_tool(tool_name)
        return await handler(request)
