from app.core.config import settings
from app.llm.llm_client import client
from app.schemas.chat import ChatResponse


class ChatService:
    """Business logic for chat."""

    def generate_response(self, prompt: str) -> ChatResponse:
        response = client.generate_response(prompt)

        return ChatResponse(
            response=response,
            model=settings.LLM_MODEL,
        )


chat_service = ChatService()