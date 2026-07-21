# Voice Assistant Frontend

React + Vite + TypeScript + Tailwind CSS UI for the voice assistant. Records
the user's voice, sends it to the backend (`/api/chat/audio`), and plays
back the synthesized reply while showing the conversation as text.

## Development

```bash
npm install
npm run dev
```

Copy `.env.example` to `.env` and adjust `VITE_BACKEND_URL` if the backend
isn't running on the default `http://localhost:8000`.

## Structure

- `src/hooks/useVoiceAssistant.ts` — the assistant's state machine (idle →
  recording → thinking → speaking → idle, or → error on failure).
- `src/hooks/useMediaRecorder.ts` — browser microphone recording, isolated
  from the state machine above.
- `src/lib/api.ts` — network client for the backend's voice endpoint.
- `src/components/` — presentational UI (mic button, status text, chat log).
