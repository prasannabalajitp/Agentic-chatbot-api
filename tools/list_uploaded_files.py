from langchain.tools import tool
from langchain_core.runnables import RunnableConfig

from tools.decorator import register_tool
from repository.file_repository import FileRepository
from core.constants import constants
from common.tool_result import ToolResult

file_repository = FileRepository()


def list_uploaded_files_impl(context: dict)->ToolResult:
    user_id = context[constants.USER_ID]
    thread_id = context[constants.THREAD_ID]

    files = file_repository.get_thread_files(
        user_id=user_id,
        thread_id=thread_id
    )
    if not files:
        return {
            constants.SUMMARY: constants.USER_DOC_EMPTY,
            constants.CITATIONS: [],
            constants.METADATA: {},
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
        f"- {file[constants.FILE_NAME]} (Uploaded: {file[constants.CREATED_AT]})"
        for file in files
    )
    return {
    constants.SUMMARY: llm_context,
    constants.CITATIONS: result,
    constants.METADATA: {}
}
    

@register_tool(name=constants.UPLD_FILES, handler=list_uploaded_files_impl, category=constants.UTLTY)
@tool
def list_uploaded_files(config: RunnableConfig):
    """
    Returns all uploaded files for the current conversation.

    Use this tool when the user asks:
    - What files have I uploaded?
    - How many documents have I uploaded?
    - What is the filename?
    - Did I upload a document?
    - Which uploaded documents are available?

    Do NOT use this tool to answer questions about document contents.
    """

    configurable = config.get(constants.CONFIGURABLE, {})

    user_id = configurable[constants.USER_ID]
    thread_id = configurable[constants.THREAD_ID]

    return list_uploaded_files_impl(user_id=user_id, thread_id=thread_id)
