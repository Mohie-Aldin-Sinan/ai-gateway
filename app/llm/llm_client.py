import json
import time
from typing import TypeVar

from openai import (
    APIConnectionError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)
from pydantic import BaseModel

from app.core.config import settings
from app.core.exceptions import LLMClientError
from app.core.logging import logger
from app.schemas.llm import CalculatorInput
from app.tools.tool_registry import TOOLS

T = TypeVar("T", bound=BaseModel)
class LLMClient:
    """Wrapper around the LLM provider SDK."""

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.BASE_URL,
            timeout=settings.LLM_TIMEOUT,
        )

    def generate_response(self, prompt: str) -> str:
        return self._generate_response_with_retry(prompt)


    def _generate_response_with_retry(self, prompt: str) -> str:
        for retry in range(settings.LLM_MAX_RETRIES + 1):
            try:
                start_time = time.perf_counter()

                response = self.client.responses.create(
                    model=settings.LLM_MODEL,
                    input=prompt,
                )

                latency = time.perf_counter() - start_time

                logger.info(
                    "LLM request completed in %.2f seconds",
                    latency,
                )

                return response.output_text

            except (RateLimitError, APIConnectionError, InternalServerError) as e:
                logger.warning(
                    "Retryable LLM error. Attempt %d/%d: %s",
                    retry + 1,
                    settings.LLM_MAX_RETRIES + 1,
                    type(e).__name__,
                )

                if retry == settings.LLM_MAX_RETRIES:
                    raise LLMClientError(
                        "LLM provider failed after maximum retries."
                    ) from e

                time.sleep(2 ** retry)

            except Exception as e:
                logger.exception("Non-retryable LLM error.")

                raise LLMClientError(
                    "Failed to communicate with the LLM provider."
                ) from e

    def generate_structured_response(
    self,
    prompt: str,
    response_model: type[T],
    ) -> T:

        for retry in range(settings.LLM_MAX_RETRIES + 1):
            try:
                response = self.client.responses.parse(
                    model=settings.LLM_MODEL,
                    input=prompt,
                    text_format=response_model,
                )

                if response.status != "completed":
                    error = response.error

                    logger.warning(
                        "Structured LLM request failed. Attempt %d/%d: %s",
                        retry + 1,
                        settings.LLM_MAX_RETRIES + 1,
                        error,
                    )

                    if retry == settings.LLM_MAX_RETRIES:
                        raise LLMClientError(
                            "Structured LLM request failed after maximum retries."
                        )

                    time.sleep(2 ** retry)
                    continue

                if response.output_parsed is None:
                    raise LLMClientError(
                        "LLM returned no structured output."
                    )

                return response.output_parsed

            except LLMClientError:
                raise

            except (RateLimitError, APIConnectionError, InternalServerError) as e:
                logger.warning(
                    "Retryable structured LLM error. Attempt %d/%d: %s",
                    retry + 1,
                    settings.LLM_MAX_RETRIES + 1,
                    type(e).__name__,
                )

                if retry == settings.LLM_MAX_RETRIES:
                    raise LLMClientError(
                        "Structured LLM request failed after maximum retries."
                    ) from e

                time.sleep(2 ** retry)

            except Exception as e:
                logger.exception("Non-retryable structured LLM error.")
                raise LLMClientError(
                    "Failed to generate structured LLM response."
                ) from e

    def request_tool_call(self, prompt: str):
        tools = [
            {
                "type": "function",
                "name": "calculator",
                "description": "Multiply two numbers.",
                "parameters": CalculatorInput.model_json_schema(),
            }
        ]

        response = self.client.responses.create(
            model=settings.LLM_MODEL,
            input=prompt,
            tools=tools,
        )

        tool_call, result = self.execute_calculator_tool(response)

        if tool_call:
            follow_up = self.client.responses.create(
                model=settings.LLM_MODEL,
                input=[
                    *response.output,
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": str(result),
                    },
                ],
            )

            return follow_up.output_text

        return response.output_text

    def execute_tool(self, tool_call):
        tool = TOOLS.get(tool_call.name)

        if tool is None:
            raise LLMClientError(
                f"Unknown tool requested: {tool_call.name}"
            )

        arguments = json.loads(tool_call.arguments)

        if tool_call.name == "calculator":
            validated_arguments = CalculatorInput.model_validate(arguments)

            return tool(
                validated_arguments.a,
                validated_arguments.b,
            )

        raise LLMClientError(
            f"No argument validator configured for: {tool_call.name}"
        )
    

client = LLMClient()