from typing import Any, Callable
from langchain.agents.middleware import AgentMiddleware
from core.constants import constants
from tools.tool_registry import registry
from guardrails.exceptions import ToolNotRegisteredError, ToolDisabledError

class ToolPolicyMiddleware(AgentMiddleware):

    def wrap_tool_call(self, request, handler):

        tool_name = request.tool_call[constants.NAME]

        metadata = registry.get_metadata(tool_name)

        if metadata is None:
            raise ToolNotRegisteredError(f"Tool '{tool_name}' is not registered.")

        if not metadata.enabled:
            raise ToolDisabledError(f"Tool '{tool_name}' is disabled.")

        return handler(request)

    async def awrap_tool_call(self, request, handler):

        tool_name = request.tool_call[constants.NAME]

        metadata = registry.get_metadata(tool_name)

        if metadata is None:
            raise RuntimeError(f"Tool '{tool_name}' is not registered.")

        if not metadata.enabled:
            raise RuntimeError(f"Tool '{tool_name}' is disabled.")

        return await handler(request)
