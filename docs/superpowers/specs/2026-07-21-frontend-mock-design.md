# Frontend Mock — Design

## Context

This is Step 4 (Fullstack — Frontend half) of the Voice AI Assistant project
(see `README.md`). Gizzat owns Frontend + ASR. The goal right now is to get a
working, deployable UI shell with a fully simulated (fake) voice interaction
flow, so the rest of the team can see and click through the intended UX
before real ASR/TTS/agent/MCP pieces exist. ASR will be implemented next,
replacing the fake data source behind a single hook.

## Goals

- A minimal, modern UI: mic button, "thinking" state, chat log with
  user/assistant messages (text duplicate of voice, per the task's
  requirement).
- The full voice-interaction flow is simulated end-to-end with fake data and
  timers — no backend, no real audio capture/playback yet.
- The fake data source is isolated behind one hook so swapping in real ASR
  later is a small, contained change.
- Deployable to Vercel so the whole team can test it in a browser without
  running anything locally.

## Non-goals

- Real microphone capture, real ASR/TTS, real backend calls, real agent/MCP
  integration — these come in later steps.
- Persisting conversation history, auth, or any backend state.

## Stack

- React + Vite + TypeScript
- Tailwind CSS
- Deployed to Vercel (static Vite build, zero extra config needed)

## Repo layout

```
frontend/
  src/
    App.tsx                  — layout: chat panel + mic button + status
    components/
      MicButton.tsx           — idle / recording / thinking / speaking visuals
      ChatPanel.tsx            — renders message bubbles (user / assistant)
      StatusBadge.tsx           — "Listening…" / "Thinking…" / "Speaking…" text + animation
    hooks/
      useVoiceAssistant.ts      — state machine: exposes { state, messages, start() }
    types.ts                    — ChatMessage, AssistantState types
  index.html
  package.json
  vite.config.ts
  tailwind.config.js
```

Frontend code lives in `/frontend` at the repo root, as a sibling to the
future `/backend` directory (Kenzhe's step).

## State machine

Owned entirely by `useVoiceAssistant`:

```
idle --click--> recording --(~2s)--> thinking --(~1.5s)--> speaking --(~2s)--> idle
```

- `start()` is called on mic button click; it drives the transitions via
  `setTimeout`.
- On entering `speaking`, the hook appends one hardcoded exchange to
  `messages`: a user message ("Привет! Куда можно сходить сегодня вечером в
  Алматы? Желательно на концерт или стендап.") and an assistant reply (the
  stand-up + jazz concert example from the task doc).
- `speaking` state drives a speaker-icon wave animation in `MicButton` — no
  real audio file is played.
- Clicking during `recording`/`thinking`/`speaking` is a no-op (button
  disabled) until back to `idle`.

## Components

- **MicButton** — circular button; visual per state:
  - `idle`: static mic icon
  - `recording`: pulsing red ring
  - `thinking`: spinner
  - `speaking`: speaker icon + subtle wave animation
- **ChatPanel** — vertical list of message bubbles, user right-aligned,
  assistant left-aligned. This satisfies the task's "duplicate by text on UI"
  requirement.
- **StatusBadge** — small text label reflecting current state ("Listening…",
  "Thinking…", "Speaking…"), hidden when `idle`.
- **App** — centered single-column layout: status + mic button on top, chat
  log below.

## Integration point for real ASR (next step)

`useVoiceAssistant` is the only module that knows the flow is currently
faked. Its public interface (`state`, `messages`, `start()`) will stay the
same when real ASR/backend calls replace the internals — no changes needed in
`App.tsx` or any component.

## Deployment

- Deployed to Vercel as a static Vite build (framework preset: Vite),
  connected to the `tazabekov/nfactorial-217-project-17-audio-models` GitHub
  repo with root directory set to `frontend/`.
- Every push to `main` produces a preview/production deployment the whole
  team can open in a browser to test the mock UI.

## Testing / verification

- Manual: run `npm run dev` locally, click the mic button, confirm the state
  machine cycles idle → recording → thinking → speaking → idle and the fake
  exchange appears in the chat log.
- Manual: after Vercel deploy, open the deployed URL and repeat the same
  check.
- No automated tests for this mock milestone (pure UI, no logic worth unit
  testing yet); real ASR step will introduce testable logic.
