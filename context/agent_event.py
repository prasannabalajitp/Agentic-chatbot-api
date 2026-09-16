from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentEventType(str, Enum):
    MODEL_START = "model_start"
    LLM_CHUNK = "llm_chunk"
    MODEL_END = "model_end"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"

@dataclass
class AgentEvent:
    type: AgentEventType
    content: str | None = None
    tool_name: str | None = None
    tool_id: str | None = None
    arguments: dict[str, Any] | None = None
    result: str | None = None
    citations: list[dict[str, Any]] = field(default_factory=list)
    has_tool_call: bool = False
