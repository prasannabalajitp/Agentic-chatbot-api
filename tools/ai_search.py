from langchain.tools import tool
from tools.decorator import register_tool
from service.retrieval_service import RetrievalService
from service.guardrail_service import GuardRailService
from repository.file_repository import FileRepository
from common.tool_result import ToolResult
from langchain_core.runnables import RunnableConfig

from core.constants import constants
from guardrails.guardrail_factory import guardrail_service

retrieval_service = RetrievalService()
file_repository = FileRepository()

def ai_search_impl(query: str,context: dict) -> ToolResult:

    user_id = context[constants.USER_ID]
    thread_id = context[constants.THREAD_ID]

    if not file_repository.has_thread_files(user_id, thread_id):
        return {
            "summary": constants.USER_DOC_EMPTY,
            "citations": [],
            "metadata": {},
        }

    documents = retrieval_service.retrieve(
        query=query,
        user_id=user_id,
        thread_id=thread_id,
    )

    if not documents:
        return {
            "summary": constants.NO_REL_DOC,
            "citations": [],
            "metadata": {},
        }

    context = "\n\n".join(
        doc["text"]
        for doc in documents
    )

    guarded_context = guardrail_service.validate_retrieval(context)
    return {
        "summary": guarded_context,
        "citations": [
            {
                "file": doc[constants.FILE_NAME],
                "chunk": doc[constants.CHUNK_IDX],
                "score": doc[constants.SCORE],
            }
            for doc in documents
        ],
        "metadata": {},
    }

@register_tool(name=constants.AI_SRCH, handler=ai_search_impl, category=constants.UTLTY)
@tool
def ai_search(query: str, config: RunnableConfig):
    """
    Search uploaded documents.

    Args:
        query: User question.
        user_id: Current user.
        thread_id: Current conversation.

    Returns:
        Relevant document chunks.
    """

    configurable = config.get(constants.CONFIGURABLE, {})

    return ai_search_impl(
        query=query,
        user_id=configurable[constants.USER_ID],
        thread_id=configurable[constants.THREAD_ID],
    )
