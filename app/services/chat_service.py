from app.agents.agent_service import AgentService
from app.core.config import settings
from app.core.dependencies import get_agent_service
from app.schemas.chat import ChatResponse


class ChatService:
    """Business logic for chat."""

    def __init__(self, agent_service: AgentService):
        self.agent_service = agent_service

    def generate_response(self, prompt: str) -> ChatResponse:
        response = self.agent_service.run(prompt)

        return ChatResponse(
            response=response,
            model=settings.LLM_MODEL,
        )


chat_service = ChatService(get_agent_service())