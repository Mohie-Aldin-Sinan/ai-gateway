from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import LLMClientError
from app.core.logging import logger


class LLMClient:
    """Wrapper around the LLM provider SDK."""

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.BASE_URL,
            timeout=30.0,
        )

    def generate_response(self, prompt: str) -> str:
        logger.info("Sending request to LLM provider.")

        try:
            response = self.client.responses.create(
                model=settings.LLM_MODEL,
                input=prompt,
            )

            logger.info("Received successful response from LLM provider.")

            return response.output_text

        except Exception as e:
            logger.exception("Failed to communicate with the LLM provider.")

            raise LLMClientError(
                "Failed to communicate with the LLM provider."
            ) from e

client = LLMClient()