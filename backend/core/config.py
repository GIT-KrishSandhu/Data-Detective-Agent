import os
from typing import List, Union
# pyrefly: ignore [missing-import]
from pydantic import AnyHttpUrl, BeforeValidator
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated

def assemble_cors_origins(v: Union[str, List[str]]) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    # General configuration
    PROJECT_NAME: str = "Data Detective Agent API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "local"  # local, staging, production

    # CORS Origins (comma separated list of hosts or json array)
    BACKEND_CORS_ORIGINS: Annotated[
        List[str], BeforeValidator(assemble_cors_origins)
    ] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "data_detective_agent"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # AI Model Configurations (Azure OpenAI or direct OpenAI API)
    # Default is OpenAI, support fallback or custom providers (agnostic agent layer)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = ""

    # Telemetry configuration
    TELEMETRY_LOG_LEVEL: str = "INFO"
    TELEMETRY_VERBOSE: bool = True

settings = Settings()
