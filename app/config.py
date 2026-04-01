from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_title: str = "FastAPI App"
    app_version: str = "0.1.0"
    app_description: str = "A FastAPI boilerplate application"

    host: str = "127.0.0.1"
    port: int = 8000
    uploads_dir: str = "uploads"


settings = Settings()
