"""Ties ASR -> Agent -> TTS together into a single voice pipeline."""
from dataclasses import dataclass

from app.services.agent import VoiceAgent
from app.services.asr import ASRService
from app.services.tts import TTSService


@dataclass
class PipelineResult:
    transcript: str
    reply_text: str
    audio_bytes: bytes
    audio_content_type: str


class VoicePipeline:
    def __init__(self, asr: ASRService, agent: VoiceAgent, tts: TTSService):
        self.asr = asr
        self.agent = agent
        self.tts = tts

    async def run_from_audio(
        self, audio_bytes: bytes, filename: str, history: list[dict] | None = None
    ) -> PipelineResult:
        transcript = await self.asr.transcribe(audio_bytes, filename)
        reply_text = await self.agent.ask(transcript, history)
        audio_out = await self.tts.synthesize(reply_text)
        return PipelineResult(
            transcript=transcript,
            reply_text=reply_text,
            audio_bytes=audio_out,
            audio_content_type=self.tts.content_type,
        )

    async def run_from_text(
        self, text: str, history: list[dict] | None = None, synthesize_audio: bool = True
    ) -> PipelineResult:
        reply_text = await self.agent.ask(text, history)
        audio_out = b""
        if synthesize_audio:
            audio_out = await self.tts.synthesize(reply_text)
        return PipelineResult(
            transcript=text,
            reply_text=reply_text,
            audio_bytes=audio_out,
            audio_content_type=self.tts.content_type,
        )
