import time

from openai import (
    APIConnectionError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)

from app.core.config import settings
from app.core.exceptions import LLMClientError
from app.core.logging import logger


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

client = LLMClient()