"""Text-to-speech providers.

The backend only depends on the ``TTSService`` interface below. The
teammate owning TTS (see project README, Step 2) can drop in a new
implementation (e.g. XTTS-v2 / Fish Speech with voice cloning) without
touching any other part of the backend -- just register it in
``get_tts_service``.
"""
from abc import ABC, abstractmethod
from functools import lru_cache

from app.config import Settings, get_settings


class TTSService(ABC):
    """Converts text into synthesized speech audio bytes."""

    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """Return audio bytes (mp3) for the given text."""
        raise NotImplementedError

    @property
    def content_type(self) -> str:
        return "audio/mpeg"


class ElevenLabsTTS(TTSService):
    """Cloud TTS via the ElevenLabs API. Low latency, great voice quality."""

    def __init__(self, api_key: str | None, voice_id: str, model_id: str):
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is required for the 'elevenlabs' TTS provider")
        self._api_key = api_key
        self._voice_id = voice_id
        self._model_id = model_id

    async def synthesize(self, text: str) -> bytes:
        import httpx

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self._voice_id}"
        headers = {
            "xi-api-key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": self._model_id,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.content


class OpenAITTS(TTSService):
    """Cloud TTS via the OpenAI TTS API."""

    def __init__(self, api_key: str | None, model: str, voice: str):
        from openai import AsyncOpenAI

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for the 'openai' TTS provider")
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._voice = voice

    async def synthesize(self, text: str) -> bytes:
        response = await self._client.audio.speech.create(
            model=self._model,
            voice=self._voice,
            input=text,
        )
        return response.read()


class MadinaTTSService(TTSService):
    """Calls Madina's standalone TTS microservice (tts/ at the repo root,
    gpt-4o-mini-tts) over HTTP instead of re-implementing it here."""

    def __init__(self, base_url: str, voice: str):
        self._base_url = base_url.rstrip("/")
        self._voice = voice

    async def synthesize(self, text: str) -> bytes:
        import httpx

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/tts/synthesize",
                json={"text": text, "voice": self._voice, "stream": False},
            )
            response.raise_for_status()
            return response.content


def _build_tts_service(settings: Settings) -> TTSService:
    if settings.tts_provider == "elevenlabs":
        return ElevenLabsTTS(
            api_key=settings.elevenlabs_api_key,
            voice_id=settings.elevenlabs_voice_id,
            model_id=settings.elevenlabs_model_id,
        )
    if settings.tts_provider == "openai":
        return OpenAITTS(
            api_key=settings.openai_api_key,
            model=settings.openai_tts_model,
            voice=settings.openai_tts_voice,
        )
    if settings.tts_provider == "madina_service":
        return MadinaTTSService(
            base_url=settings.madina_tts_url,
            voice=settings.madina_tts_voice,
        )
    raise ValueError(f"Unknown TTS provider: {settings.tts_provider}")


@lru_cache
def get_tts_service() -> TTSService:
    return _build_tts_service(get_settings())
