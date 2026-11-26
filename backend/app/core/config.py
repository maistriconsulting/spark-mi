from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "SPARK-MI"
    app_env: str = "development"
    app_debug: bool = False
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    frontend_url: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173"
    db_host: str
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: str
    db_ssl: bool = True
    jwt_secret_key: str
    access_token_expire_minutes: int = 30
    bootstrap_token: str = ""
    log_level: str = "INFO"

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("JWT_SECRET_KEY must contain at least 32 characters")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
