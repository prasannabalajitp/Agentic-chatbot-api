from uuid import uuid4

from langchain_core.messages import ToolMessage

from common.state import AgentState
from common.tool_result import ToolResult
from tools.tool_registry import registry
from core.constants import constants


def executor(state: AgentState):

    plan = state.get(constants.PLAN)

    if not plan or not plan.get(constants.NEED_TOOLS, False):
        return {}

    context = {
        constants.USER_ID: state[constants.USER_ID],
        constants.THREAD_ID: state[constants.THREAD_ID],
    }

    tool_messages = []
    all_citations = []
    all_tool_results = []
    get_all_Tools = registry.get_all()

    for tool_spec in plan.get(constants.TOOLS, []):

        tool_name = tool_spec[constants.TOOL]
        tool_args = tool_spec.get(constants.ARGS1, {})

        handler = registry.get_handler(tool_name)
        if handler is None:
            raise ValueError(f"Unknown tool: {tool_name}")

        try:
            result: ToolResult = handler(
                **tool_args,
                context=context,
            )

        except Exception as ex:
            result = {
                "summary": f"Tool '{tool_name}' failed: {str(ex)}",
                "citations": [],
                "metadata": {},
            }
            all_tool_results.append(
                {
                    "tool": tool_name,
                    "args": tool_args,
                    "summary": "",
                    "citations": [],
                    "metadata": {},
                    "status": "failed",
                    "error": str(ex),
                }
            )

            tool_messages.append(
                ToolMessage(
                    content=result["summary"],
                    name=tool_name,
                    tool_call_id=f"planner-{uuid4()}",
                )
            )

            continue

        tool_message = ToolMessage(
            content=result.get("summary", ""),
            name=tool_name,
            tool_call_id=f"planner-{uuid4()}",
        )

        tool_messages.append(tool_message)

        all_citations.extend(
            result.get("citations", [])
        )

        all_tool_results.append(
            {
                "tool": tool_name,
                "args": tool_args,
                "summary": result.get("summary", ""),
                "citations": result.get("citations", []),
                "metadata": result.get("metadata", {}),
                "status": "success",
            }
        )

    existing_tool_results = state.get("tool_results", [])
    existing_citations = state.get("citations", [])

    return {
        "messages": tool_messages,
        "citations": existing_citations + all_citations,
        "tool_results": existing_tool_results + all_tool_results,
    }
