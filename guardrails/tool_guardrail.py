from fastapi import HTTPException
from core.constants import constants
from .exceptions import ToolExecutionLimitError

class ToolGuardrail:
    MAX_TOOL_CALLS = 5
    def validate(self, tool_name: str, tool_calls_count: int):
        if tool_calls_count > self.MAX_TOOL_CALLS:
            raise HTTPException(
                status_code=400,
                detail=constants.MNY_TOOL_CALL
            )
        return True

    def validate_call_count(self, tool_calls_count: int) -> None:
        if tool_calls_count >= self.MAX_TOOL_CALLS:
            raise ToolExecutionLimitError(
                "Maximum tool-call limit exceeded."
            )
