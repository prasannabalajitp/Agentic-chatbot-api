from guardrails.prompt_guardrail import PromptGuardrail, OutputGuardrail
from guardrails.tool_guardrail import ToolGuardrail
from guardrails.retrieval_guardrail import RetrievalGuardrail


class GuardRailService:

    def __init__(self, llm):
        self.prompt_guardrail = PromptGuardrail(llm)
        self.output_guardrail = OutputGuardrail(llm)
        self.tool_guardrail = ToolGuardrail()
        self.retrieval_guardrail = RetrievalGuardrail()

    def validate_prompt(self, query):
        self.prompt_guardrail.validate(query)

    def validate_tool(self, tool_name, tool_calls):
        self.tool_guardrail.validate(tool_name, tool_calls)

    def validate_retrieval(self, text):
        return self.retrieval_guardrail.validate(text)

    def validate_response(self, response):
        return self.output_guardrail.validate(response)
