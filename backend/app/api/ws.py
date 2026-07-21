"""Bonus: real-time ASR over WebSocket.

The client streams raw audio chunks (webm/opus or wav, small slices) as
binary WebSocket frames. We buffer them and re-transcribe the accumulated
audio with faster-whisper after every chunk, pushing back a partial
transcript as JSON so the frontend can show live text while the user is
still speaking. The client sends the text frame "__end__" to signal the
end of the utterance.
"""
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.asr import FasterWhisperASR
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/asr")
async def websocket_asr(websocket: WebSocket) -> None:
    await websocket.accept()
    settings = get_settings()
    asr = FasterWhisperASR(
        model_size=settings.faster_whisper_model_size,
        device=settings.faster_whisper_device,
        compute_type=settings.faster_whisper_compute_type,
    )
    buffer = bytearray()
    try:
        while True:
            message = await websocket.receive()
            if message.get("bytes") is not None:
                buffer.extend(message["bytes"])
                if len(buffer) == 0:
                    continue
                try:
                    partial_text = await asr.transcribe(bytes(buffer), "chunk.webm")
                except Exception:
                    logger.exception("Partial transcription failed")
                    continue
                await websocket.send_text(
                    json.dumps({"type": "partial", "text": partial_text})
                )
            elif message.get("text") == "__end__":
                final_text = ""
                if buffer:
                    final_text = await asr.transcribe(bytes(buffer), "final.webm")
                await websocket.send_text(json.dumps({"type": "final", "text": final_text}))
                buffer.clear()
    except WebSocketDisconnect:
        logger.info("ASR websocket client disconnected")
