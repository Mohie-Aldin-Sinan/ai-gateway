from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User prompt sent to the LLM",
    )


class ChatResponse(BaseModel):
    response: str
    model: str