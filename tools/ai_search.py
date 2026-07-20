from langchain.tools import tool
from service.retrieval_service import RetrievalService

from core.constants import constants

retrieval_service = RetrievalService()

@tool
def ai_search(query: str, user_id: str,thread_id: str):
    """
    Search uploaded documents.

    Args:
        query: User question.
        user_id: Current user.
        thread_id: Current conversation.

    Returns:
        Relevant document chunks.
    """

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
