from app.agents.agent_service import agent_service

result = agent_service.run(
    "Search for information about FastAPI."
)

print(result)