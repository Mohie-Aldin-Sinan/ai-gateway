import json

from app.core.exceptions import LLMClientError
from app.core.logging import logger
from app.tools.tool_registry import TOOLS


class ToolExecutor:
    """Executes tools requested by the LLM."""

    def execute(self, tool_call):
        logger.info(
            "Tool requested: %s | arguments: %s",
            tool_call.name,
            tool_call.arguments,
        )

        tool = TOOLS.get(tool_call.name)

        if tool is None:
            logger.error(
                "Unknown tool requested: %s",
                tool_call.name,
            )
            raise LLMClientError(
                f"Unknown tool requested: {tool_call.name}"
            )

        arguments = json.loads(tool_call.arguments)

        validated_arguments = tool["schema"].model_validate(arguments)

        result = tool["function"](
            **validated_arguments.model_dump()
        )

        logger.info(
            "Tool executed successfully: %s | result: %s",
            tool_call.name,
            result,
        )

        return result


tool_executor = ToolExecutor()