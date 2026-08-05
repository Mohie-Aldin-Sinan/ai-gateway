from app.core.config import settings
from app.llm.llm_client import LLMClient, client
from app.schemas.chat import ChatResponse


class ChatService:
    """Business logic for chat."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate_response(self, prompt: str) -> ChatResponse:
        response = self.llm_client.generate_response(prompt)

        return ChatResponse(
            response=response,
            model=settings.LLM_MODEL,
        )


chat_service = ChatService(client)