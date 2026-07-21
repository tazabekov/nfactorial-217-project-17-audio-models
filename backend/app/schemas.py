"""Pydantic request/response models for the API."""
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class TextChatRequest(BaseModel):
    text: str
    history: list[ChatMessage] = []
    synthesize_audio: bool = True


class ChatResult(BaseModel):
    transcript: str
    reply_text: str


class HealthResponse(BaseModel):
    status: str
    asr_provider: str
    tts_provider: str
    llm_provider: str
    mcp_enabled: bool
