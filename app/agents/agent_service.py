from app.llm.llm_client import LLMClient
from app.tools.tool_executor import ToolExecutor
from app.tools.tool_registry import get_tool_definitions


class AgentService:
    """Coordinates LLM calls and tool execution."""

    def __init__(
        self,
        llm_client: LLMClient,
        tool_executor: ToolExecutor,
    ):
        self.llm_client = llm_client
        self.tool_executor = tool_executor

    def run(self, prompt: str) -> str:
        tools = get_tool_definitions()

        response = self.llm_client.create_response(
            prompt,
            tools=tools,
        )

        tool_call = next(
            (
                item
                for item in response.output
                if item.type == "function_call"
            ),
            None,
        )

        if not tool_call:
            return response.output_text

        result = self.tool_executor.execute(tool_call)

        follow_up = self.llm_client.create_response(
            [
                *response.output,
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(result),
                },
            ]
        )

        return follow_up.output_text


