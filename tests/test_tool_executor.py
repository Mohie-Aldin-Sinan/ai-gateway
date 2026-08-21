from app.tools.tool_executor import ToolExecutor


class FakeToolCall:
    name = "calculator"
    arguments = '{"a": 25, "b": 4}'


def test_tool_executor_executes_calculator():
    executor = ToolExecutor()

    tool_call = FakeToolCall()

    result = executor.execute(tool_call)

    assert result == 100