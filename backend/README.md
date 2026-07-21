# Backend — Voice AI Assistant

FastAPI service that orchestrates the full voice pipeline:

```
audio in --> ASR --> LangChain agent (+ MCP Playwright tools) --> TTS --> audio out
```

This is the **Step 4 (Backend)** piece of the group project (see the root
[README](../README.md) for the full task and team assignments). ASR
(Step 1), TTS (Step 2), and the MCP Playwright agent tooling (Step 3) are
built by teammates — the backend defines small provider interfaces so each
piece can be swapped in independently.

## Layout

```
backend/
  app/
    main.py               FastAPI app, CORS, router wiring
    config.py              Settings (env vars / .env)
    schemas.py              Request/response models
    api/
      routes.py            POST /api/chat/audio, POST /api/chat/text, GET /api/health
      ws.py                 WS /ws/asr (bonus: real-time streaming ASR)
      deps.py                DI: builds the VoicePipeline
    services/
      asr.py                ASRService interface + OpenAI Whisper / faster-whisper
      tts.py                 TTSService interface + ElevenLabs / OpenAI TTS
      agent.py                VoiceAgent: LangGraph react-agent + MCP Playwright tools
      orchestrator.py         VoicePipeline: ties asr -> agent -> tts together
  tests/
  requirements.txt
  .env.example
  Dockerfile
```

## Running locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in the API keys you want to use
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for interactive API docs.

## API

- `GET /api/health` — provider/config sanity check.
- `POST /api/chat/audio` — multipart upload (`file`), full voice round trip.
  Returns the synthesized reply audio (`audio/mpeg`) with the recognized
  transcript and the agent's reply text echoed back in the URL-encoded
  `X-Transcript` / `X-Agent-Reply` response headers.
- `POST /api/chat/text` — JSON `{ "text": "...", "history": [...] }`, same
  response shape as above. Handy for testing the agent/TTS without a
  microphone, and for frontend development.
- `WS /ws/asr` — bonus real-time ASR: stream binary audio chunks, get back
  `{"type": "partial", "text": "..."}` messages as the model transcribes,
  then send the text frame `"__end__"` to get a `{"type": "final", ...}`.

## Swapping providers

Every external dependency sits behind a small interface, selected via env
vars in `config.py`:

| Concern | Env var | Options |
|---|---|---|
| ASR | `ASR_PROVIDER` | `openai` (Whisper API, default), `faster_whisper` (local) |
| TTS | `TTS_PROVIDER` | `elevenlabs` (default), `openai` |
| LLM | `LLM_PROVIDER` | `openai` (default), `anthropic` |
| MCP Playwright | `MCP_ENABLED`, `MCP_PLAYWRIGHT_COMMAND`, `MCP_PLAYWRIGHT_ARGS` | any stdio MCP server command |

To add a new provider, implement the relevant `ABC` in `services/asr.py` or
`services/tts.py` and add a branch in that file's `_build_*_service`
function — nothing else needs to change.

The agent (`services/agent.py`) degrades gracefully to a tool-less LLM if
the MCP Playwright server fails to start, so the rest of the pipeline keeps
working while that piece is under development.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```
