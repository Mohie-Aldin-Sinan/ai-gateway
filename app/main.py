from fastapi import FastAPI

from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="A production-ready FastAPI backend for building scalable LLM applications.",
    version=settings.APP_VERSION,
)

app.include_router(health_router)
app.include_router(chat_router)