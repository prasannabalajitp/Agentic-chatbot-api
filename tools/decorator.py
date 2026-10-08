from tools.tool_registry import ToolRisk, registry
from core.constants import constants

def register_tool(name: str, handler, category: str = constants.GEN, risk: ToolRisk = ToolRisk.LOW, requires_confirmation: bool = False, max_calls_per_run: int = 5):
    def decorator(tool):
        registry.register(
            name=name,
            tool=tool,
            handler=handler,
            category=category,
            risk=risk,
            requires_confirmation=requires_confirmation,
            max_calls_per_run=max_calls_per_run,
        )
        return tool
    
    return decorator
