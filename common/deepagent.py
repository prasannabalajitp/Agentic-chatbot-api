from deepagents import create_deep_agent, HarnessProfile, register_harness_profile
from llm.nvidia_llm import llm
from tools.tool_registry import registry
from database.checkpointer import checkpointer
from core.constants import constants
from core.config import settings
from common.prompt import SYSTEM_PROMPT
from datetime import datetime, timezone

register_harness_profile(
    settings.HARNESS_MODEL,
    HarnessProfile(
        excluded_tools=frozenset(constants.FROZENSET),
    ),
)

tools = registry.get_all()
current_datetime = (datetime.now(timezone.utc).isoformat())

prompt = f"""
Current datetime:
{current_datetime}

{SYSTEM_PROMPT}
"""

deep_agent = create_deep_agent(
    model=llm,
    tools=tools,
    system_prompt=prompt,
    checkpointer=checkpointer
)

def invoke_deepagent(query: str, user_id: str, thread_id: str):
    config = {
        constants.CONFIGURABLE:{
            constants.USER_ID: user_id,
            constants.THREAD_ID: thread_id
        }
    }

    return deep_agent.invoke({
            constants.MESSAGES: {
                constants.ROLE: constants.USER,
                constants.CONTENT: query
            }
        },
        config=config
    )
