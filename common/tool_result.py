from typing import TypedDict, Any

class ToolResult(TypedDict):
    summary: str
    citations: list[Any]
    metadata: dict[str, Any]
