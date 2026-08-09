from typing import TypedDict, Annotated, Any

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    plan: dict | None
    user_id: str
    thread_id: str
    current_step: int
    tool_results: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    reflection: dict | None
