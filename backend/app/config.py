"""Central configuration for the backend, read from environment variables / .env."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- General ---
    app_name: str = "Voice Assistant Backend"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- LLM (agent brain) ---
    llm_provider: str = "openai"  # "openai" | "anthropic"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    # --- ASR (speech-to-text) ---
    asr_provider: str = "openai"  # "openai" | "faster_whisper"
    asr_model: str = "whisper-1"
    faster_whisper_model_size: str = "small"
    faster_whisper_device: str = "cpu"
    faster_whisper_compute_type: str = "int8"

    # --- TTS (text-to-speech) ---
    tts_provider: str = "elevenlabs"  # "elevenlabs" | "openai"
    elevenlabs_api_key: str | None = None
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_model_id: str = "eleven_multilingual_v2"
    openai_tts_model: str = "tts-1"
    openai_tts_voice: str = "alloy"

    # --- MCP Playwright (web search tool for the agent) ---
    mcp_playwright_command: str = "npx"
    mcp_playwright_args: list[str] = ["-y", "@playwright/mcp@latest"]
    mcp_enabled: bool = True

    agent_system_prompt: str = (
        "You are a friendly voice assistant that helps the user plan their "
        "leisure time (evenings, weekends, going out). When the user asks about "
        "events, concerts, movies, exhibitions or tickets, use your web browsing "
        "tools to check real event listing sites (e.g. sxodim.com, kino.kz, "
        "ticketon.kz) for up to date information instead of guessing. Keep answers "
        "short, natural and spoken-friendly, since they will be read aloud by a "
        "text-to-speech engine. Reply in the same language the user used."
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
