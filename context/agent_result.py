from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    response: str
    citations: list[dict[str, Any]] = field(default_factory=list)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
