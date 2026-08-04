from openai import OpenAI

from app.core.config import settings


class LLMClient:
    """Wrapper around the LLM provider SDK."""

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.BASE_URL,
        )

    def generate_response(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=settings.LLM_MODEL,
            input=prompt,
        )

        return response.output_text

client = LLMClient()