import json, re
from fastapi import HTTPException
from langchain_core.messages import HumanMessage, SystemMessage

from guardrails.prompts import PROMPT_GUARDRAIL, OUTPUT_GUARDRAIL
from core.constants import constants

class PromptGuardrail:

    def __init__(self, llm):
        self.llm = llm


    def _looks_suspicious(self, query: str) -> bool:

        patterns = [
            r"ignore.*instruction",
            r"forget.*instruction",
            r"system.*prompt",
            r"developer.*message",
            r"hidden.*instruction",
            r"reveal.*prompt",
            r"show.*prompt",
            r"show.*instruction",
            r"disable.*tool",
            r"enable.*tool",
            r"bypass.*policy",
            r"override.*instruction",
            r"act as.*assistant",
            r"pretend.*assistant",
            r"you are now",
            r"new instructions",
            r"jailbreak",
        ]

        q = query.lower()

        return any(
            re.search(pattern, q)
            for pattern in patterns
        )

    def validate(self, query: str):
        query = query.lower()
        if not self._looks_suspicious(query):
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
            reason = response.get(constants.REASON)
            print(f"[PROMPT GUARDRAIL] Blocked: {reason}")
            raise HTTPException(
                status_code=400,
                detail=constants.UNSFE_PRMPT
            )
        category = response.get(constants.CATEGORY)

        if category not in constants.ALLOWED_GUARDRAILS:
            raise HTTPException(
                status_code=500,
                detail=constants.INVLD_GURDRL_RES
            )
        confidence = response.get(constants.CONFIDENCE, 0)
        if confidence < 0.75:
            raise HTTPException(
                status_code=400,
                detail=constants.UNABLE_CNFDNT_VALIDATE
            )
        return response


class OutputGuardrail:

    def __init__(self, llm):
        self.llm = llm


    def _looks_sensitive(self, response: str) -> bool:

        patterns = [
            r"system\s*prompt",
            r"developer\s*message",
            r"hidden\s*instruction",
            r"chain\s*of\s*thought",
            r"internal\s*instruction",
            r"api[_ ]?key",
            r"secret[_ ]?key",
            r"bearer\s+[A-Za-z0-9\-_.]+",
            r"traceback",
            r"stack\s*trace",
            r"exception",
            r"tool\s*registry",
            r"internal\s*tool",
        ]

        text = response.lower()

        return any(
            re.search(pattern, text)
            for pattern in patterns
        )

    def validate(self, response: str):
        lower = response.lower()

        for term in constants.BLOCKED_TERMS:
            if term in lower:
                raise HTTPException(
                    status_code=500,
                    detail=constants.UNSFE_RESP
                )

        # Fast path
        if not self._looks_sensitive(response):
            return response

        messages = [
            SystemMessage(content=OUTPUT_GUARDRAIL),
            HumanMessage(content=response)
        ]

        result = self.llm.invoke(messages)

        try:
            validation = json.loads(result.content)

        except Exception:
            raise HTTPException(
                status_code=500,
                detail=constants.UNBLE_MDL_RES
            )

        if not validation.get(constants.ALLWD, False):

            raise HTTPException(
                status_code=500,
                detail=validation.get(
                    constants.REASON,
                    constants.UNSFE_RESP
                )
            )

        return response
