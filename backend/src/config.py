from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    nextauth_secret: Optional[str] = None
    api_host: Optional[str] = "localhost"
    api_port: Optional[str] = "8000"
    next_public_api_url: Optional[str] = "http://localhost:8000"
    db_echo: bool = False  # Set to True to see SQL queries in logs

    class Config:
        env_file = ".env"


settings = Settings()