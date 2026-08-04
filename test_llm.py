from app.llm.llm_client import llm_client

response = llm_client.generate_response(
    "Say hello in one sentence."
)

print(response)