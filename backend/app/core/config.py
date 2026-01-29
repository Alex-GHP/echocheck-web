from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from env variables"""

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "echocheck"

    hf_model_name: str = "alxdev/echocheck-political-stance"

    api_title: str = "EchoCheck API"
    api_version: str = "1.0.0"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
