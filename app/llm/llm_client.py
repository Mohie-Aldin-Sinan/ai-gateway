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

T = TypeVar("T", bound=BaseModel)
class LLMClient:
    """Wrapper around the LLM provider SDK."""

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.BASE_URL,
            timeout=settings.LLM_TIMEOUT,
        )

    def create_response(self, input, tools=None):
        kwargs = {
            "model": settings.LLM_MODEL,
            "input": input,
        }

        if tools is not None:
            kwargs["tools"] = tools

        return self.client.responses.create(**kwargs)

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


    
client = LLMClient()