"""HTTP API: audio in -> audio out, plus a text-only endpoint for debugging
without a microphone."""
import logging
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response

from app.api.deps import get_pipeline
from app.config import Settings, get_settings
from app.schemas import HealthResponse, TextChatRequest
from app.services.orchestrator import VoicePipeline

logger = logging.getLogger(__name__)
router = APIRouter()


def _audio_response(result) -> Response:
    return Response(
        content=result.audio_bytes,
        media_type=result.audio_content_type or "audio/mpeg",
        headers={
            "X-Transcript": quote(result.transcript),
            "X-Agent-Reply": quote(result.reply_text),
        },
    )


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        asr_provider=settings.asr_provider,
        tts_provider=settings.tts_provider,
        llm_provider=settings.llm_provider,
        mcp_enabled=settings.mcp_enabled,
    )


@router.post("/chat/audio")
async def chat_audio(
    file: UploadFile,
    pipeline: VoicePipeline = Depends(get_pipeline),
) -> Response:
    """Full voice round trip: audio in, audio out.

    Returns the synthesized reply audio as the response body. The
    recognized transcript and the agent's reply text are echoed back in the
    ``X-Transcript`` / ``X-Agent-Reply`` headers (URL-encoded) so the
    frontend can display them alongside playback.
    """
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio upload")

    try:
        result = await pipeline.run_from_audio(audio_bytes, file.filename or "audio.wav")
    except Exception as exc:
        logger.exception("Voice pipeline failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return _audio_response(result)


@router.post("/chat/text")
async def chat_text(
    payload: TextChatRequest,
    pipeline: VoicePipeline = Depends(get_pipeline),
) -> Response:
    """Text in, audio (+ headers) out. Useful for testing the agent/TTS
    without recording audio, and for frontend development/mocking."""
    history = [message.model_dump() for message in payload.history]
    try:
        result = await pipeline.run_from_text(
            payload.text, history=history, synthesize_audio=payload.synthesize_audio
        )
    except Exception as exc:
        logger.exception("Voice pipeline failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return _audio_response(result)
