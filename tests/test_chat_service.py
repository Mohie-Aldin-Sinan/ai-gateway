import pytest

from app.core.exceptions import LLMClientError
from app.services.chat_service import ChatService


class FakeAgentService:
    def __init__(self, should_fail=False):
        self.received_prompt = None
        self.should_fail = should_fail

    def run(self, prompt: str) -> str:
        self.received_prompt = prompt

        if self.should_fail:
            raise LLMClientError("LLM provider failed.")

        return "This is a fake response."


def test_generate_response():
    fake_agent = FakeAgentService()
    service = ChatService(fake_agent)

    result = service.generate_response("Hello")

    assert result.response == "This is a fake response."
    assert fake_agent.received_prompt == "Hello"


def test_generate_response_when_llm_fails():
    fake_agent = FakeAgentService(should_fail=True)
    service = ChatService(fake_agent)

    with pytest.raises(LLMClientError):
        service.generate_response("Hello")