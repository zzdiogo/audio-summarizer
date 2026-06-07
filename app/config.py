from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Whisper
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    # LLM (OpenAI ou compatível)
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    # Ollama (alternativa local, sem custo)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    llm_provider: str = "openai"  # "openai" ou "ollama"

    # API
    max_upload_size_mb: int = 100
    allowed_extensions: str = ".mp3,.wav,.m4a,.ogg,.flac,.webm,.mp4"


@lru_cache
def get_settings() -> Settings:
    return Settings()
