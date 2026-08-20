from app.schemas.llm import CalculatorInput, SearchInput
from app.tools.calculator import calculator
from app.tools.search import search

TOOLS = {
    "calculator": {
        "function": calculator,
        "schema": CalculatorInput,
        "description": "Multiply two numbers.",
    },
    "search": {
        "function": search,
        "schema": SearchInput,
        "description": "Search for information using a mock search service.",
    },
}

def get_tool_definitions():
    return [
        {
            "type": "function",
            "name": name,
            "description": config["description"],
            "parameters": config["schema"].model_json_schema(),
        }
        for name, config in TOOLS.items()
    ]