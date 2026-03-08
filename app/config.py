"""Lightweight, dependency-free settings loader.

This module intentionally avoids importing `pydantic` or
`pydantic-settings` to sidestep compatibility issues in dev
environments. It reads config from environment variables with
reasonable defaults.
"""

from functools import lru_cache
import os


def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    try:
        return int(v) if v is not None else default
    except Exception:
        return default


class Settings:
    # App
    APP_NAME: str = os.getenv("APP_NAME", "Mémoire de Parfum")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    DEBUG: bool = _env_bool("DEBUG", False)

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = _env_int("API_PORT", 8000)

    # LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_MAX_TOKENS: int = _env_int("LLM_MAX_TOKENS", 2048)
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    # Per-request timeout for OpenAI API (seconds); pipeline has 2 LLM calls so frontend should allow ~2x this
    LLM_REQUEST_TIMEOUT: int = _env_int("LLM_REQUEST_TIMEOUT", 90)

    # Postgres
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "memoire")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "memoire_pass")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "memoire_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = _env_int("POSTGRES_PORT", 5432)

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "neo4j_pass")

    # Weaviate
    WEAVIATE_HOST: str = os.getenv("WEAVIATE_HOST", "localhost")
    WEAVIATE_PORT: int = _env_int("WEAVIATE_PORT", 8080)

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = _env_int("REDIS_PORT", 6379)
    REDIS_TTL_SECONDS: int = _env_int("REDIS_TTL_SECONDS", 3600)

    # Auth
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = _env_int("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60)

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = _env_int("RATE_LIMIT_PER_MINUTE", 20)

    # LangSmith / Tracing
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "memoire-de-parfum")

    @property
    def LANGCHAIN_TRACING_V2(self) -> bool:
        explicit = _env_bool("LANGCHAIN_TRACING_V2", True)
        key = self.LANGCHAIN_API_KEY
        if not key or key.startswith("your-") or key == "":
            return False
        return explicit


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
