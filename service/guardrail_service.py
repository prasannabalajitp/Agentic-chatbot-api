from guardrails.prompt_guardrail import PromptGuardrail, OutputGuardrail
from guardrails.tool_guardrail import ToolGuardrail


class GuardRailService:

    def __init__(self, llm):
        self.prompt_guardrail = PromptGuardrail(llm)
        self.output_guardrail = OutputGuardrail()
        self.tool_guardrail = ToolGuardrail()

    def validate_prompt(self, query):
        self.prompt_guardrail.validate(query)

    def validate_tool(self, tool_name, tool_calls):
        self.tool_guardrail.validate(tool_name, tool_calls)

    def validate_response(self, response):
        return self.output_guardrail.validate(response)
