"""FastAPI dependency providers."""
from functools import lru_cache

from app.services.agent import get_voice_agent
from app.services.asr import get_asr_service
from app.services.orchestrator import VoicePipeline
from app.services.tts import get_tts_service


@lru_cache
def get_pipeline() -> VoicePipeline:
    return VoicePipeline(
        asr=get_asr_service(),
        agent=get_voice_agent(),
        tts=get_tts_service(),
    )
