from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field

from .service import VOICES, DEFAULT_VOICE, DEFAULT_INSTRUCTIONS, synthesize, synthesize_stream

router = APIRouter(prefix="/tts", tags=["TTS"])


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096, description="Text to convert to speech")
    voice: str = Field(DEFAULT_VOICE, description=f"Voice to use: {VOICES}")
    stream: bool = Field(False, description="Stream audio in real-time")
    instructions: str = Field(DEFAULT_INSTRUCTIONS, description="Style instructions for the voice")


@router.post(
    "/synthesize",
    responses={
        200: {"content": {"audio/mpeg": {}}, "description": "MP3 audio file"},
    },
    summary="Convert text to speech",
)
async def synthesize_speech(req: TTSRequest):
    """
    Convert text to speech using gpt-4o-mini-tts.
    Returns MP3 audio — either as a full file or as a stream.
    """
    if req.voice not in VOICES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid voice '{req.voice}'. Choose from: {VOICES}",
        )

    if req.stream:
        return StreamingResponse(
            synthesize_stream(req.text, req.voice, req.instructions),
            media_type="audio/mpeg",
            headers={"X-Voice": req.voice, "X-Model": "gpt-4o-mini-tts"},
        )

    audio_bytes = synthesize(req.text, req.voice, req.instructions)
    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"X-Voice": req.voice, "X-Model": "gpt-4o-mini-tts"},
    )


@router.get("/voices", summary="List available voices")
async def list_voices():
    """Return all supported TTS voices."""
    return {
        "voices": VOICES,
        "default": DEFAULT_VOICE,
        "model": "gpt-4o-mini-tts",
    }
