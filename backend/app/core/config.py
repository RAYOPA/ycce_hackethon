import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ManRakshak API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Analytics Privacy
    ANALYTICS_MIN_COHORT_SIZE: int = 5
    # Rate Limiting
    RATE_LIMIT_LOGIN: int = 5 # requests per minute
    
    # CORS
    CORS_ORIGINS: str = "" # Comma separated list. Use * for all in dev if needed, but not allowed with allow_credentials=True in prod
    
    # AI Gateway Settings
    AI_PROVIDER: str = "openrouter"
    OPEN_ROUTER_API_KEY: str = ""
    OPEN_ROUTER_API: str = "" # Alias/fallback for OPEN_ROUTER_API in .env
    OPEN_ROUTER_MODEL: str = "qwen/qwen3.8-27b:free"
    OPEN_ROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    AI_REQUEST_TIMEOUT_SECONDS: float = 30.0
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def effective_openrouter_api_key(self) -> str:
        return self.OPEN_ROUTER_API_KEY.strip() or self.OPEN_ROUTER_API.strip() or ""

settings = Settings()

