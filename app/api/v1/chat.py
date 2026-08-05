from fastapi import APIRouter, HTTPException

from app.core.exceptions import LLMClientError
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return chat_service.generate_response(request.prompt)

    except LLMClientError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        ) from e

