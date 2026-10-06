from dataclasses import dataclass, field
from typing import Any

@dataclass
class AgentContext:
    user_id: str
    thread_id: str
    query: str
    uploaded_files: list[Any] = field(default_factory=list)
