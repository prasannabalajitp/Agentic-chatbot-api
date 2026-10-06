from langchain.tools import tool
from tools.decorator import register_tool
from service.retrieval_service import RetrievalService
from service.guardrail_service import GuardRailService
from repository.file_repository import FileRepository
from common.tool_result import ToolResult
from langchain_core.runnables import RunnableConfig

from core.constants import constants
from guardrails.guardrail_factory import guardrail_service

import logging

logger = logging.getLogger(__name__)

retrieval_service = RetrievalService()
file_repository = FileRepository()

def ai_search_impl(query: str,context: dict) -> ToolResult:

    user_id = context[constants.USER_ID]
    thread_id = context[constants.THREAD_ID]

    if not file_repository.has_thread_files(user_id, thread_id):
        return {
            constants.SUMMARY: constants.USER_DOC_EMPTY,
            constants.CITATIONS: [],
            constants.METADATA: {},
        }

    documents = retrieval_service.retrieve(
        query=query,
        user_id=user_id,
        thread_id=thread_id,
    )

    if not documents:
        return {
            constants.SUMMARY: constants.NO_REL_DOC,
            constants.CITATIONS: [],
            constants.METADATA: {},
        }

    context_text = "\n\n".join(
        doc[constants.TXT]
        for doc in documents
    )

    guarded_context = guardrail_service.validate_retrieval(context_text)
    return {
        constants.SUMMARY: guarded_context,
        constants.CITATIONS: [
            {
                constants.FILE: doc[constants.FILE_NAME],
                constants.CHUNK: doc[constants.CHUNK_IDX],
                constants.SCORE: doc[constants.SCORE],
            }
            for doc in documents
        ],
        constants.METADATA: {},
    }

@register_tool(name=constants.AI_SRCH,  handler=ai_search_impl, category=constants.UTLTY,)
@tool
def ai_search(query: str, config: RunnableConfig):
    """
    Search uploaded documents.
    """

    configurable = config.get(constants.CONFIGURABLE, {})
    context = {
        constants.USER_ID: configurable[constants.USER_ID],
        constants.THREAD_ID: configurable[constants.THREAD_ID],
    }
    return ai_search_impl(
        query=query,
        context=context,
    )
