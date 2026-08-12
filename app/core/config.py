from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Gateway"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    OPENROUTER_API_KEY: str
    LLM_MODEL: str = "gpt-oss-20b:free"

    BASE_URL: str = "https://openrouter.ai/api/v1"

    LLM_MAX_RETRIES: int = 2

    LLM_TIMEOUT: float = 30.0

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()