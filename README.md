# 🎙 Voice AI Assistant with Web Search (Group Project)

Build a full voice-based AI assistant that talks to the user by voice (with a text
duplicate in the UI) and can browse the web via **MCP Playwright** to look up
real-world information.

The project combines audio models (Speech-to-Text, Text-to-Speech), an
LLM-based agent (LangChain), the Model Context Protocol (MCP), and classic
fullstack development.

## Project info

- **Team size:** 3-4 people
- **Duration:** TBD
- **Recommended stack:** Python (FastAPI / LangChain), React / Vue / Vanilla JS
  for the frontend, Playwright, Whisper (or similar), ElevenLabs.

## 🎯 Goal: Voice Assistant for Leisure Planning

Build a web app that the user talks to **only by voice**. The main use case is
an assistant that helps plan a day, evening, or weekend out: it searches for
tickets, checks event/movie/exhibition schedules, and suggests options.

### User flow

1. The user presses a button and speaks into the microphone: *"Hi! Where can I
   go tonight in Almaty? Ideally a concert or stand-up."*
2. The system captures the audio and converts speech to text (ASR).
3. The text is sent to the LLM agent (built with LangChain).
4. The agent autonomously realizes it needs a fresh listing of events. It uses
   the **MCP Playwright** tool to open a site such as `sxodim.com/almaty`,
   `kino.kz`, `ticketon.kz` (or any other sites you choose to scrape), reads
   the page, and collects relevant events for the evening.
5. The agent produces a final text answer.
6. The text answer is converted to speech (TTS) and played back automatically:
   *"Tonight there's a great stand-up show on Abay street at 19:00 and a jazz
   concert at 20:00. Which one would you like?"*

```
Voice AI Assistant - Pipeline
End-to-end flow: Voice In -> AI -> Voice Out

Frontend (UI)              Backend (Server)              External (Web)
User -> Microphone -> audio -> ASR (Whisper) -> text
                                -> LangChain Agent + LLM -- MCP --> MCP Playwright (Browser)
                                                        <-- events --      |
                                answer <- TTS (ElevenLabs)                v
Speaker <- audio <-------------------                    sxodim.com / ticketon.kz / kino.kz
Chat UI (text) <-------------------
```

## 👥 Team & assignments

| Step | Area | Owner |
|------|------|-------|
| 1 | ASR / STT | Gizzat |
| 2 | TTS | Madina |
| 3 | MCP Playwright (web data retrieval) | Kassiyet |
| 4 | Backend | Kenzhe |
| 4 | Frontend | Gizzat |

## 🛠 Technical requirements & the 4 work steps

The project splits naturally into **4 steps**, one per team member.

### Step 1 — Speech Recognition (ASR / STT)

Convert the user's audio into text.

- **Cloud APIs:** OpenAI Whisper API, Google Speech-to-Text, AssemblyAI.
- **Local models:**
  - `nvidia/parakeet-tdt-0.6b-v3` — great performance and speed.
  - `openai/whisper-large-v3-turbo` — optimized version of the strongest
    Whisper model.
  - `Systran/faster-whisper-small` — CTranslate2 implementation of Whisper,
    much faster than the original library with minimal memory usage.

> **Hyperparameter tips (Whisper-based ASR):**
> - `beam_size`: default 5. Lowering it (e.g. to 1, "greedy search") speeds up
>   inference but may slightly reduce quality.
> - `temperature`: keep at `0.0` for the most accurate transcription. If the
>   model hallucinates or loops, try a list of values (e.g. `[0.0, 0.2, 0.4]`)
>   so it searches over more likely paths.
> - `condition_on_previous_text`: if the model gets "stuck" repeating the last
>   phrase (common on long audio), try setting this to `False`. You lose a bit
>   of context but gain stability.

### Step 2 — Speech Synthesis (TTS)

Make the agent's text answer sound natural.

- **Cloud APIs:** ElevenLabs API (best voice quality, low-latency streaming),
  OpenAI TTS.
- **Local / open-source models:**
  - `fishaudio/s2-pro` (Fish Speech) — excellent voice quality with voice
    cloning.
  - `coqui-ai/XTTS-v2` — strong Russian and English support, voice cloning,
    streaming generation.
  - `suno/bark` or modern alternatives like OuteTTS (GPU resources permitting).

### Step 3 — The assistant's brain: LangChain Agent + MCP Playwright

- **Foundation:** build the agent using **LangChain**.
- **Tools:** the key requirement — the agent must use an **MCP server** for
  Playwright.
- **Behavior:** the agent must be smart enough to figure out *which specific
  websites (event listings)* to visit based on the user's request. Put
  together a list of target source sites and teach the agent to search them
  for current events.

### Step 4 — Fullstack wrapper (Frontend + Backend)

- **Backend:** orchestrates everything — receives audio, calls ASR, passes the
  text to the MCP-enabled agent, sends the generated text to TTS, and returns
  the resulting audio file/stream to the client.
- **Frontend:** a modern, minimal UI. A record button, a nice "thinking"
  animation while the agent works, and audio playback.

## ✅ Definition of Done

1. **End-to-end flow works:** you can ask something by voice and get a voice
   answer back.
2. **MCP Playwright integrated:** the agent successfully handles requests that
   require browsing the web (e.g. searching events on sites like
   sxodim.com).
3. **Audio quality:** ASR works reliably and TTS voice quality is good.
4. **Code organization:** code is well structured, backend and frontend are
   separated, API design is sensible.
5. **Teamwork:** Git is used properly (branching, PRs), regular commits from
   all team members.

## 🌟 Bonus (Advanced / Real-time)

For extra points and a more responsive system:

1. **Real-time ASR via WebSocket:** run a lightweight local model (e.g.
   `faster-whisper-small`) and stream audio from the frontend to the backend
   over WebSocket, transcribing and showing text live while the user is still
   speaking.
2. **Streaming TTS:** stream audio back to the frontend (ElevenLabs API
   Streaming or a local model like XTTS-v2 / Fish Speech) so the agent's
   answer starts playing as it's generated, without waiting for the full
   response.
