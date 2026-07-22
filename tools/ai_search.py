from langchain.tools import tool
from tools.decorator import register_tool
from service.retrieval_service import RetrievalService
from langchain_core.runnables import RunnableConfig

from core.constants import constants

retrieval_service = RetrievalService()

@register_tool(name=constants.AI_SRCH, category=constants.UTLTY)
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

    user_id = configurable[constants.USER_ID]
    thread_id = configurable[constants.THREAD_ID]

    documents = retrieval_service.retrieve(query=query, user_id=user_id, thread_id=thread_id)

    if not documents:
        return constants.NO_REL_DOC
    
    context = []
    
    for doc in documents:
        context.append(
            f"""File: {doc['file_name']}
            Chunk: {doc['chunk_index']}
            Score: {doc['score']:.2f}

            {doc['text']}
            """
                )
    return "\n\n---\n\n".join(context)
