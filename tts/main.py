from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .router import router as tts_router

app = FastAPI(
    title="Voice AI Assistant — TTS Service",
    description="Text-to-Speech module using gpt-4o-mini-tts",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts_router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "TTS", "model": "gpt-4o-mini-tts"}
