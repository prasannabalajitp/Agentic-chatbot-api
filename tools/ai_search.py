import logging

from langchain.tools import tool
from langchain_core.runnables import RunnableConfig

from common.tool_result import ToolResult
from core.constants import constants
from exceptions.database import DatabaseError
from exceptions.external_service import ExternalServiceError
from guardrails.guardrail_factory import guardrail_service
from repository.file_repository import FileRepository
from service.retrieval_service import RetrievalService
from tools.decorator import register_tool
from tools.tool_registry import ToolRisk

logger = logging.getLogger(__name__)

retrieval_service = RetrievalService()
file_repository = FileRepository()


def _failure_response(message: str) -> ToolResult:
    return {
        constants.SUMMARY: message,
        constants.CITATIONS: [],
        constants.METADATA: {
            constants.SUCC: False,
            constants.RETRYABLE: True,
        },
    }


def ai_search_impl(query: str, context: dict) -> ToolResult:
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

    if not query or not query.strip():
        return {
            constants.SUMMARY: "Please provide a question to search for.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }

    try:
        has_files = file_repository.has_thread_files(user_id, thread_id)

        if not has_files:
            return {
                constants.SUMMARY: constants.USER_DOC_EMPTY,
                constants.CITATIONS: [],
                constants.METADATA: {
                    constants.SUCC: True,
                },
            }

        documents = retrieval_service.retrieve(
            query=query,
            user_id=user_id,
            thread_id=thread_id,
        )

    except DatabaseError:
        return _failure_response("Uploaded documents could not be searched right now.")
    except ExternalServiceError:
        return _failure_response("Document search is temporarily unavailable.")
    except Exception:
        return _failure_response("Document search could not be completed.")

    if not documents:
        return {
            constants.SUMMARY: constants.NO_REL_DOC,
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: True,
            },
        }

    context_text = "\n\n".join(
        doc[constants.TXT] for doc in documents
    )

    guarded_context = guardrail_service.validate_retrieval(context_text)

    citations = [
        {
            constants.FILE: doc[constants.FILE_NAME],
            constants.CHUNK: doc[constants.CHUNK_IDX],
            constants.SCORE: doc[constants.SCORE],
        }
        for doc in documents
    ]

    return {
        constants.SUMMARY: guarded_context,
        constants.CITATIONS: citations,
        constants.METADATA: {
            constants.SUCC: True,
            constants.RESULT_CNT: len(documents),
        },
    }


@register_tool(name=constants.AI_SRCH, handler=ai_search_impl, category=constants.UTLTY, risk=ToolRisk.MEDIUM)
@tool
def ai_search(query: str, config: RunnableConfig) -> ToolResult:
    """Search uploaded documents for information relevant to the query."""
    configurable = config.get(constants.CONFIGURABLE, {})
    context = {
        constants.USER_ID: configurable.get(constants.USER_ID),
        constants.THREAD_ID: configurable.get(constants.THREAD_ID),
    }
    return ai_search_impl(query=query, context=context)
