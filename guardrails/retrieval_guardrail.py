import re
from core.constants import constants

class RetrievalGuardrail:
    def validate(self, text):

        MAX_CONTEXT = 10000
        if len(text) > MAX_CONTEXT:
            text = text[:MAX_CONTEXT]

        dangerous = constants.DNGRS_GUARDRAIL

        for item in dangerous:
            text = re.sub(item, constants.EMPTY_STRING, text, flags=re.IGNORECASE)

        return text
