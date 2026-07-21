import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
DEFAULT_VOICE = "nova"
MODEL = "gpt-4o-mini-tts"

# Instructions to make the assistant sound warm and natural in Russian/English
DEFAULT_INSTRUCTIONS = (
    "Speak warmly and naturally, like a friendly assistant. "
    "When speaking Russian, use a clear and natural Kazakh-Russian accent. "
    "Keep a conversational, helpful tone."
)


def synthesize(
    text: str,
    voice: str = DEFAULT_VOICE,
    instructions: str = DEFAULT_INSTRUCTIONS,
    output_format: str = "mp3",
) -> bytes:
    """Convert text to speech and return raw audio bytes."""
    if voice not in VOICES:
        voice = DEFAULT_VOICE

    response = client.audio.speech.create(
        model=MODEL,
        voice=voice,
        input=text,
        instructions=instructions,
        response_format=output_format,
    )
    return response.content


def synthesize_to_file(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    instructions: str = DEFAULT_INSTRUCTIONS,
) -> Path:
    """Convert text to speech and save to a file."""
    audio_bytes = synthesize(text, voice, instructions)
    path = Path(output_path)
    path.write_bytes(audio_bytes)
    return path


def synthesize_stream(
    text: str,
    voice: str = DEFAULT_VOICE,
    instructions: str = DEFAULT_INSTRUCTIONS,
):
    """Stream audio chunks for real-time playback."""
    if voice not in VOICES:
        voice = DEFAULT_VOICE

    with client.audio.speech.with_streaming_response.create(
        model=MODEL,
        voice=voice,
        input=text,
        instructions=instructions,
        response_format="mp3",
    ) as response:
        for chunk in response.iter_bytes(chunk_size=4096):
            yield chunk
