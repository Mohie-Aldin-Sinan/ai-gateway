from app.agents.agent_service import agent_service
from app.core.config import settings
from app.schemas.chat import ChatResponse


class ChatService:
    """Business logic for chat."""

    def generate_response(self, prompt: str) -> ChatResponse:
        response = agent_service.run(prompt)

        return ChatResponse(
            response=response,
            model=settings.LLM_MODEL,
        )


chat_service = ChatService()