import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env"
        )
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/aiti_guru"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
    
settings = Settings()


def setup_logging() -> None:
    """Настройка корневого лдоггера из конфига"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=settings.LOG_FORMAT,
    )
    