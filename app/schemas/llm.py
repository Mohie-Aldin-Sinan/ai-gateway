from pydantic import BaseModel


class LLMResponse(BaseModel):
    answer: str
    confidence: float 

class CalculatorInput(BaseModel):
    a: float
    b: float

class SearchInput(BaseModel):
    query: str