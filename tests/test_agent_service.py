from app.agents.agent_service import AgentService


class FakeResponse:
    def __init__(self, output=None, output_text="Final answer"):
        self.output = output or []
        self.output_text = output_text


class FakeLLMClient:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def create_response(self, input, tools=None):
        self.calls.append({
            "input": input,
            "tools": tools,
        })

        return self.responses.pop(0)


class FakeToolCall:
    type = "function_call"
    name = "calculator"
    call_id = "call_123"
    arguments = '{"a": 25, "b": 4}'


class FakeToolExecutor:
    def __init__(self):
        self.executed_tool = None

    def execute(self, tool_call):
        self.executed_tool = tool_call
        return 100


def test_agent_returns_llm_response_without_tool_call():
    llm = FakeLLMClient(
        [
            FakeResponse(
                output=[],
                output_text="Hello from the LLM",
            )
        ]
    )

    executor = FakeToolExecutor()

    agent = AgentService(
        llm_client=llm,
        tool_executor=executor,
    )

    result = agent.run("Hello")

    assert result == "Hello from the LLM"
    assert len(llm.calls) == 1
    assert executor.executed_tool is None


def test_agent_executes_tool_and_sends_result_back_to_llm():
    tool_call = FakeToolCall()

    llm = FakeLLMClient(
        [
            FakeResponse(
                output=[tool_call],
                output_text="",
            ),
            FakeResponse(
                output=[],
                output_text="The answer is 100.",
            ),
        ]
    )

    executor = FakeToolExecutor()

    agent = AgentService(
        llm_client=llm,
        tool_executor=executor,
    )

    result = agent.run("What is 25 multiplied by 4?")

    assert result == "The answer is 100."

   
    assert executor.executed_tool is tool_call

    assert len(llm.calls) == 2

    second_input = llm.calls[1]["input"]

    assert {
        "type": "function_call_output",
        "call_id": "call_123",
        "output": "100",
    } in second_input