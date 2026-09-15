from dataclasses import dataclass

@dataclass
class AgentEvent:
    type: str
    content: str | None = None
    tool_name: str | None = None
    tool_id: str | None = None
    arguments: dict | None = None
    result: str | None = None
    citations: list | None = None
    has_tool_call: bool = False
