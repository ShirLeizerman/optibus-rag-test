from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # AI provider selection:
    # auto   -> OpenAI when a key exists, otherwise local/offline
    # openai -> force OpenAI and fail if no key exists
    # local  -> force fully offline mode
    ai_mode: Literal["auto", "openai", "local"] = "auto"

    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"

    top_k: int = 3

    # Local hashed embeddings have a different score distribution
    # from OpenAI embeddings, so each provider gets its own threshold.
    local_similarity_threshold: float = 0.12
    openai_similarity_threshold: float = 0.30

    max_query_length: int = 2000
    max_context_chars: int = 12000

    embedding_cache_dir: str = "data/embeddings"

    # Vite local dev + Docker frontend
    frontend_origins: str = (
        "http://localhost:5173,http://localhost:3000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    def resolve_ai_mode(self) -> str:
        if self.ai_mode == "local":
            return "local"

        if self.ai_mode == "openai":
            if not self.openai_api_key:
                raise RuntimeError(
                    "AI_MODE=openai requires OPENAI_API_KEY."
                )
            return "openai"

        # auto mode
        if self.openai_api_key:
            return "openai"

        return "local"

    def get_frontend_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]


settings = Settings()