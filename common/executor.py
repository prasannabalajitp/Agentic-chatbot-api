from uuid import uuid4

from langchain_core.messages import ToolMessage

from common.state import AgentState
from common.tool_result import ToolResult
from tools.tool_registry import registry
from core.constants import constants
from guardrails.guardrail_factory import guardrail_service
import logging

logger = logging.getLogger(__name__)


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

    existing_tool_results = state.get(constants.TOOL_RES, [])
    executed_results = existing_tool_results.copy()
    # tool_call_count = state.get(constants.TOOL_COUNT, 0)
    tool_call_count = 0

    for tool_spec in plan.get(constants.TOOLS, []):

        tool_name = tool_spec[constants.TOOL]
        tool_args = tool_spec.get(constants.ARGS1, {})


        duplicate = any(
            item.get(constants.TOOL) == tool_name
            and item.get(constants.ARGS1, {}) == tool_args
            and item.get(constants.FILE_STATUS) == constants.SUCC
            for item in executed_results
        )

        if duplicate:
            logger.info("Skipping duplicate tool call: %s %s", tool_name, tool_args)        
            continue

        tool_call_count += 1
        guardrail_service.validate_tool(tool_name=tool_name, tool_calls=tool_call_count)

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
                constants.SUMMARY: f"Tool '{tool_name}' failed: {str(ex)}",
                constants.CITATIONS: [],
                constants.METADATA: {},
            }
            all_tool_results.append(
                {
                    constants.TOOL: tool_name,
                    constants.ARGS1: tool_args,
                    constants.SUMMARY: "",
                    constants.CITATIONS: [],
                    constants.METADATA: {},
                    constants.FILE_STATUS: "failed",
                    constants.ERR: str(ex),
                }
            )

            tool_messages.append(
                ToolMessage(
                    content=result[constants.SUMMARY],
                    name=tool_name,
                    tool_call_id=f"planner-{uuid4()}",
                )
            )

            continue

        tool_message = ToolMessage(
            content=result.get(constants.SUMMARY, constants.EMPTY_STRING),
            name=tool_name,
            tool_call_id=f"planner-{uuid4()}",
        )
        logger.info("========== EXECUTOR RESULT ==========")
        
        logger.info("TOOL: %s", tool_name)

        logger.info("RESULT: %s", result)
        logger.info("SUMMARY: %s", repr(result.get("summary", "")))
        logger.info("======================================")
        tool_messages.append(tool_message)
        all_citations.extend(
            result.get(constants.CITATIONS, [])
        )

        all_tool_results.append(
            {
                constants.TOOL: tool_name,
                constants.ARGS1: tool_args,
                constants.SUMMARY: result.get(constants.SUMMARY, ""),
                constants.CITATIONS: result.get(constants.CITATIONS, []),
                constants.METADATA: result.get(constants.METADATA, {}),
                constants.FILE_STATUS: constants.SUCC,
            }
        )

        executed_results.append({
                constants.TOOL: tool_name,
                constants.ARGS1: tool_args,
                constants.FILE_STATUS: constants.SUCC,
        })

    existing_citations = state.get(constants.CITATIONS, [])

    return {
        constants.MESSAGES: tool_messages,
        constants.CITATIONS: existing_citations + all_citations,
        constants.TOOL_RES: existing_tool_results + all_tool_results,
        constants.TOOL_COUNT: tool_call_count
    }
