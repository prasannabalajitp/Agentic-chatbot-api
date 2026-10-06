from typing import Literal
from pydantic import BaseModel, Field


ToolName = Literal[
    "calculator_tool",
    "current_datetime",
    "web_search",
    "ai_search",
    "list_uploaded_files",
    "yfinance_tool",
]

class ToolCall(BaseModel):
    tool: ToolName
    args: dict = Field(default_factory=dict)


class Plan(BaseModel):
    needs_tools: bool
    tools: list[ToolCall] = Field(default_factory=list)
    reason: str = ""
