from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str | None = None

    openai_embedding_model: str = (
        "text-embedding-3-small"
    )

    openai_chat_model: str = "gpt-4o-mini"

    use_mock_ai: bool = True

    top_k: int = 3

    similarity_threshold: float = 0.45

    max_query_length: int = 2000

    max_context_chars: int = 12000

    frontend_origin: str = (
        "http://localhost:3000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
