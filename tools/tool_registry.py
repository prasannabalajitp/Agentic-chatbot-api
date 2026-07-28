from dataclasses import dataclass
from core.constants import constants
from typing import Any


@dataclass
class ToolMetaData:
    name: str
    tool: Any
    category: str
    enabled: bool = True


class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, ToolMetaData] = {}

    def register(self, name: str, tool: Any, category: str = constants.GEN, enabled: bool = True) -> None:
        self._tools[name] = ToolMetaData(
            name=name,
            tool=tool,
            category=category,
            enabled=enabled
        )

    
    def get_all(self) -> list[Any]:
        return [
            tool.tool
            for tool in self._tools.values()
            if tool.enabled
        ]
    
    def get(self, name: str):
        metadata = self._tools.get(name)
        return metadata.tool if metadata else None
    
    def list(self) -> list[ToolMetaData]:
        return list(self._tools.values())

    def enable(self, name: str):
        if name in self._tools:
            self._tools[name].enabled = True

    def disable(self, name: str):
        if name in self._tools:
            self._tools[name].enabled = False


registry = ToolRegistry()
