from langchain.tools import tool
from langchain_core.runnables import RunnableConfig

from common.tool_result import ToolResult
from core.constants import constants
from exceptions.database import DatabaseError
from repository.file_repository import FileRepository
from tools.decorator import register_tool
from tools.tool_registry import ToolRisk


file_repository = FileRepository()


def list_uploaded_files_impl(context: dict) -> ToolResult:
    user_id = context.get(constants.USER_ID)
    thread_id = context.get(constants.THREAD_ID)

    if not user_id or not thread_id:
        return {
            constants.SUMMARY: "Unable to identify the current conversation.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }

    try:
        files = file_repository.get_thread_files(
            user_id=user_id,
            thread_id=thread_id,
        )
    except DatabaseError:
        return {
            constants.SUMMARY: "Uploaded files could not be retrieved right now.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: True,
            },
        }
    except Exception:
        return {
            constants.SUMMARY: "Uploaded files could not be retrieved right now.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: True,
            },
        }

    if not files:
        return {
            constants.SUMMARY: constants.USER_DOC_EMPTY,
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: True,
            },
        }

    result = [
        {
            constants.FILE_ID: file[constants.FILE_ID],
            constants.FILE_NAME: file[constants.FILE_NAME],
            constants.CREATED_AT: str(file[constants.CREATED_AT]),
        }
        for file in files
    ]

    llm_context = "Uploaded documents:\n\n" + "\n".join(
        f"- {file[constants.FILE_NAME]} "
        f"(Uploaded: {file[constants.CREATED_AT]})"
        for file in files
    )

    return {
        constants.SUMMARY: llm_context,
        constants.CITATIONS: result,
        constants.METADATA: {
            constants.SUCC: True,
            constants.RESULT_CNT: len(files),
        },
    }


@register_tool(name=constants.UPLD_FILES, handler=list_uploaded_files_impl, category=constants.UTLTY, risk=ToolRisk.LOW)
@tool
def list_uploaded_files(config: RunnableConfig) -> ToolResult:
    """List the documents uploaded to the current conversation.

    Use this tool for questions about uploaded filenames or file counts.
    Do not use it to answer questions about document contents.
    """
    configurable = config.get(constants.CONFIGURABLE, {})
    context = {
        constants.USER_ID: configurable.get(constants.USER_ID),
        constants.THREAD_ID: configurable.get(constants.THREAD_ID),
    }
    return list_uploaded_files_impl(context=context)
