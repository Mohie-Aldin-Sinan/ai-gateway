from app.agents.agent_service import AgentService
from app.llm.llm_client import client
from app.tools.tool_executor import tool_executor


def get_agent_service() -> AgentService:
    return AgentService(
        llm_client=client,
        tool_executor=tool_executor,
    )