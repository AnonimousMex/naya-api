from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env", env_ignore_empty=True, extra="ignore"
    )

    # API Configuration
    API_V1: str
    PROJECT_NAME: str

    # Sentry (todos opcionales: si SENTRY_DSN está vacío, Sentry se desactiva)
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "local"
    SENTRY_RELEASE: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.2
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.0

    # Database Configuration
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int

    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    # Redis Configuration
    REDIS_HOST: str
    REDIS_PORT: int

    # Email Configuration
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
