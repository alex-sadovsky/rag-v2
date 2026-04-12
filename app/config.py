from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_title: str = "FastAPI App"
    app_version: str = "0.1.0"
    app_description: str = "A FastAPI boilerplate application"

    host: str = "127.0.0.1"
    port: int = 8000
    uploads_dir: str = "uploads"

    anthropic_api_key: str | None = ""
    anthropic_model: str = "claude-haiku-4-5"

    # Conditional hybrid retrieval: BM25 only when dense is "weak" AND lexical warrant passes.
    # Chroma returns lower-is-better distance (L2 on embedding vectors). If the best hit distance
    # is above this threshold, dense matches are treated as weak (conservative default).
    query_dense_weak_best_distance_gt: float = Field(default=1.5, gt=0)
    query_lexical_min_alpha_tokens: int = Field(default=5, ge=1)
    query_lexical_enable_quotes: bool = True
    query_lexical_enable_identifiers: bool = True


settings = Settings()
