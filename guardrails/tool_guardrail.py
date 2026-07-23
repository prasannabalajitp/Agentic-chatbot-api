from fastapi import HTTPException
from core.constants import constants

class ToolGuardrail:

    MAX_TOOL_CALLS = 5

    def validate(self, tool_name: str, tool_calls_count: list):

        if tool_calls_count > self.MAX_TOOL_CALLS:

            raise HTTPException(
                status_code=400,
                detail=constants.MNY_TOOL_CALL
            )

        return True
