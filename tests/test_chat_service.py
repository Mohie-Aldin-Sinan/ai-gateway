import pytest

from app.core.exceptions import LLMClientError
from app.services.chat_service import ChatService


class FakeLLMClient:
    def __init__(self, should_fail=False):
        self.received_prompt = None
        self.should_fail = should_fail

    def generate_response(self, prompt: str) -> str:
        self.received_prompt = prompt

        if self.should_fail:
            raise LLMClientError("LLM provider failed.")

        return "This is a fake response."


def test_generate_response():
    fake_client = FakeLLMClient()
    service = ChatService(fake_client)

    result = service.generate_response("Hello")

    assert result.response == "This is a fake response."
    assert fake_client.received_prompt == "Hello"


def test_generate_response_when_llm_fails():
    fake_client = FakeLLMClient(should_fail=True)
    service = ChatService(fake_client)

    with pytest.raises(LLMClientError):
        service.generate_response("Hello")