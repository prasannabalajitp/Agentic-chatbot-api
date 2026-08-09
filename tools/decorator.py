from tools.tool_registry import registry
from core.constants import constants

def register_tool(name: str, handler, category: str = constants.GEN):
    def decorator(tool):
        registry.register(
            name=name,
            tool=tool,
            handler=handler,
            category=category
        )
        return tool
    
    return decorator
