from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"
    FRONTEND_URL: str
    LOG_DIR: str
    ANTHROPIC_API_KEY: Optional[str] = None
    HF_API_TOKEN: Optional[str] = None
    HF_MODEL: Optional[str] = None
    HF_ENDPOINT: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
