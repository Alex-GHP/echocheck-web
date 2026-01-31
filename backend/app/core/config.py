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

    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    resend_api_key: str = "re_your_api_key_here"
    resend_from_email: str = "onboarding@resend.dev"

    verification_code_expire_minutes: int = 10
    verification_code_length: int = 6

    max_file_size_mb: int = 10
    allowed_file_extensions: list[str] = [".txt", ".pdf", ".docx"]

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
