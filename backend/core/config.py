from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "NourisHer"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    FRONTEND_URL: str = "http://localhost:3000"

    DATABASE_URL: str = "postgresql+asyncpg://nourisher:password@localhost:5432/nourisher_db"
    SYNC_DATABASE_URL: str = "postgresql://nourisher:password@localhost:5432/nourisher_db"

    JWT_SECRET_KEY: str = "change-me-jwt"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    ANTHROPIC_API_KEY: str = ""

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@nourisherapp.com"

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
