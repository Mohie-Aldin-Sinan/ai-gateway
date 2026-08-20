import json

from app.core.exceptions import LLMClientError
from app.tools.tool_registry import TOOLS


class ToolExecutor:
    """Executes tools requested by the LLM."""

    def execute(self, tool_call):
        tool = TOOLS.get(tool_call.name)

        if tool is None:
            raise LLMClientError(
                f"Unknown tool requested: {tool_call.name}"
            )

        arguments = json.loads(tool_call.arguments)

        validated_arguments = tool["schema"].model_validate(arguments)

        return tool["function"](
            **validated_arguments.model_dump()
        )

tool_executor = ToolExecutor()