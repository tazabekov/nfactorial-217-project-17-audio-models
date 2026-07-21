"""Speech-to-text providers.

The backend only depends on the ``ASRService`` interface below. The
teammate owning ASR (see project README, Step 1) can drop in a new
implementation (e.g. a local nvidia/parakeet or faster-whisper-large model)
without touching any other part of the backend -- just register it in
``get_asr_service``.
"""
from abc import ABC, abstractmethod
from functools import lru_cache
from io import BytesIO

from app.config import Settings, get_settings


class ASRService(ABC):
    """Converts raw audio bytes into text."""

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """Return the transcript for the given audio bytes."""
        raise NotImplementedError


class OpenAIWhisperASR(ASRService):
    """Cloud ASR via the OpenAI Whisper API. Good default, needs no local GPU."""

    def __init__(self, api_key: str | None, model: str = "whisper-1"):
        from openai import AsyncOpenAI

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for the 'openai' ASR provider")
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        buffer = BytesIO(audio_bytes)
        buffer.name = filename
        result = await self._client.audio.transcriptions.create(
            model=self._model,
            file=buffer,
        )
        return result.text.strip()


class FasterWhisperASR(ASRService):
    """Local ASR via faster-whisper (CTranslate2). Runs fully offline.

    Hyperparameters follow the project's recommendations: beam_size=5,
    temperature=0.0 (falls back to a small ladder on failure), and
    condition_on_previous_text=False for stability on longer clips.
    """

    def __init__(self, model_size: str, device: str, compute_type: str):
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._model = None

    def _ensure_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self._model_size, device=self._device, compute_type=self._compute_type
            )
        return self._model

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        import asyncio
        import tempfile
        from pathlib import Path

        def _run() -> str:
            model = self._ensure_model()
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir) / filename
                tmp_path.write_bytes(audio_bytes)
                segments, _info = model.transcribe(
                    str(tmp_path),
                    beam_size=5,
                    temperature=[0.0, 0.2, 0.4],
                    condition_on_previous_text=False,
                )
                return "".join(segment.text for segment in segments).strip()

        return await asyncio.to_thread(_run)


def _build_asr_service(settings: Settings) -> ASRService:
    if settings.asr_provider == "openai":
        return OpenAIWhisperASR(api_key=settings.openai_api_key, model=settings.asr_model)
    if settings.asr_provider == "faster_whisper":
        return FasterWhisperASR(
            model_size=settings.faster_whisper_model_size,
            device=settings.faster_whisper_device,
            compute_type=settings.faster_whisper_compute_type,
        )
    raise ValueError(f"Unknown ASR provider: {settings.asr_provider}")


@lru_cache
def get_asr_service() -> ASRService:
    return _build_asr_service(get_settings())
