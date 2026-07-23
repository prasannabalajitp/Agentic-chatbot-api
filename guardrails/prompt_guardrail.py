import json
from fastapi import HTTPException
from langchain_core.messages import HumanMessage, SystemMessage

from guardrails.prompts import PROMPT_GUARDRAIL
from core.constants import constants

class PromptGuardrail:

    def __init__(self, llm):
        self.llm = llm

    def validate(self, query: str):
        query = query.lower()
        if not any(p in query for p in constants.SUSPICIOUS_PATTERNS):
            return
        messages = [
            SystemMessage(content=PROMPT_GUARDRAIL),
            HumanMessage(content=query)
        ]
        result = self.llm.invoke(messages)

        try:
            response = json.loads(result.content)
        except Exception:

            raise HTTPException(
                status_code=500,
                detail=constants.UNABLE_VALIDATE
            )

        if not response.get(constants.ALLWD, False):

            raise HTTPException(
                status_code=400,
                detail=response.get(
                    constants.REASON,
                    constants.UNSFE_PRMPT
                )
            )


class OutputGuardrail:

    def validate(self, response: str):
        lower = response.lower()

        for term in constants.BLOCKED_TERMS:
            if term in lower:
                raise HTTPException(
                    status_code=500,
                    detail=constants.UNSFE_RESP
                )

        return response
