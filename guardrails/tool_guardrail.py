from .exceptions import ToolExecutionLimitError

class ToolGuardrail:
    MAX_TOOL_CALLS = 5
    def validate_call_count(self, tool_calls_count: int) -> None:
        if tool_calls_count >= self.MAX_TOOL_CALLS:
            raise ToolExecutionLimitError(
                "Maximum tool-call limit exceeded."
            )
