# Frontend Mock Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deployable React + Vite + Tailwind UI that simulates the full voice-interaction flow (idle → recording → thinking → speaking → idle) with fake, hardcoded data, isolated behind one hook so real ASR can replace it later without touching the UI.

**Architecture:** A single hook (`useVoiceAssistant`) owns a fake state machine driven by `setTimeout`s; three presentational components (`MicButton`, `StatusBadge`, `ChatPanel`) render off its output; `App.tsx` composes them. No backend calls exist yet.

**Tech Stack:** React 18, Vite, TypeScript, Tailwind CSS v4 (via `@tailwindcss/vite` plugin — no `tailwind.config.js`/`postcss.config.js` needed), deployed to Vercel.

## Global Constraints

- Frontend code lives in `/frontend` at the repo root (sibling to future `/backend`).
- Tailwind CSS v4 installed via the `@tailwindcss/vite` plugin — CSS is imported with `@import "tailwindcss";`, no separate config files.
- State machine timings: `recording` 2000ms, `thinking` 1500ms, `speaking` 2000ms, then back to `idle`.
- Fake exchange text (exact strings, from the task doc):
  - User: `Привет! Куда можно сходить сегодня вечером в Алматы? Желательно на концерт или стендап.`
  - Assistant: `Сегодня вечером есть классный стендап на Абая в 19:00 и джазовый концерт в 20:00. Куда бы ты хотел?`
- No automated test framework for this milestone (spec-approved decision) — each task's "test cycle" is `npm run build` (TypeScript correctness) plus a manual dev-server check.
- Mic button is disabled (no-op) whenever `state !== 'idle'`.
- Deployment target: Vercel, framework preset Vite, project root directory `frontend/`.

---

### Task 1: Scaffold Vite + React + TypeScript project with Tailwind CSS

**Files:**
- Create: `frontend/` (via `npm create vite`)
- Modify: `frontend/vite.config.ts`
- Modify: `frontend/src/index.css`

**Interfaces:**
- Produces: a working Vite dev server at `frontend/`, Tailwind utility classes available in any `.tsx` file under `frontend/src`.

- [ ] **Step 1: Scaffold the Vite React-TS project**

Run from the repo root:
```bash
npm create vite@latest frontend -- --template react-ts
```

- [ ] **Step 2: Install dependencies**

```bash
cd frontend
npm install
```

- [ ] **Step 3: Install Tailwind CSS and its Vite plugin**

```bash
npm install tailwindcss @tailwindcss/vite
```

- [ ] **Step 4: Register the Tailwind Vite plugin**

Replace the contents of `frontend/vite.config.ts` with:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

- [ ] **Step 5: Import Tailwind in the main stylesheet**

Replace the entire contents of `frontend/src/index.css` with:

```css
@import "tailwindcss";
```

- [ ] **Step 6: Verify the build compiles**

```bash
npm run build
```
Expected: build completes with no errors, `frontend/dist/` is created.

- [ ] **Step 7: Verify the dev server serves Tailwind-styled content**

```bash
npm run dev &
sleep 2
curl -s http://localhost:5173 | grep -q "<div id=\"root\">" && echo OK
kill %1
```
Expected: prints `OK`.

- [ ] **Step 8: Commit**

```bash
cd ..
git add frontend
git commit -m "Scaffold Vite + React + TypeScript frontend with Tailwind CSS"
```

---

### Task 2: Shared types and the fake voice-assistant state machine hook

**Files:**
- Create: `frontend/src/types.ts`
- Create: `frontend/src/hooks/useVoiceAssistant.ts`

**Interfaces:**
- Consumes: nothing (pure React/TypeScript, no external deps beyond React).
- Produces:
  - `AssistantState = 'idle' | 'recording' | 'thinking' | 'speaking'`
  - `ChatMessage { id: string; role: 'user' | 'assistant'; text: string }`
  - `useVoiceAssistant(): { state: AssistantState; messages: ChatMessage[]; start: () => void }`

- [ ] **Step 1: Create the shared types**

Create `frontend/src/types.ts`:

```typescript
export type AssistantState = 'idle' | 'recording' | 'thinking' | 'speaking';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
}
```

- [ ] **Step 2: Implement the fake state machine hook**

Create `frontend/src/hooks/useVoiceAssistant.ts`:

```typescript
import { useCallback, useState } from 'react';
import type { AssistantState, ChatMessage } from '../types';

const FAKE_EXCHANGE = {
  user: 'Привет! Куда можно сходить сегодня вечером в Алматы? Желательно на концерт или стендап.',
  assistant: 'Сегодня вечером есть классный стендап на Абая в 19:00 и джазовый концерт в 20:00. Куда бы ты хотел?',
};

const RECORDING_MS = 2000;
const THINKING_MS = 1500;
const SPEAKING_MS = 2000;

interface UseVoiceAssistantResult {
  state: AssistantState;
  messages: ChatMessage[];
  start: () => void;
}

export function useVoiceAssistant(): UseVoiceAssistantResult {
  const [state, setState] = useState<AssistantState>('idle');
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const start = useCallback(() => {
    setState((current) => {
      if (current !== 'idle') return current;

      setTimeout(() => {
        setState('thinking');

        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            { id: `${Date.now()}-user`, role: 'user', text: FAKE_EXCHANGE.user },
            { id: `${Date.now()}-assistant`, role: 'assistant', text: FAKE_EXCHANGE.assistant },
          ]);
          setState('speaking');

          setTimeout(() => {
            setState('idle');
          }, SPEAKING_MS);
        }, THINKING_MS);
      }, RECORDING_MS);

      return 'recording';
    });
  }, []);

  return { state, messages, start };
}
```

- [ ] **Step 3: Verify the build compiles**

```bash
cd frontend
npm run build
```
Expected: build completes with no TypeScript errors.

- [ ] **Step 4: Commit**

```bash
cd ..
git add frontend/src/types.ts frontend/src/hooks/useVoiceAssistant.ts
git commit -m "Add fake voice-assistant state machine hook"
```

---

### Task 3: MicButton component

**Files:**
- Create: `frontend/src/components/MicButton.tsx`

**Interfaces:**
- Consumes: `AssistantState` from `frontend/src/types.ts` (Task 2).
- Produces: `MicButton({ state: AssistantState; onClick: () => void })` — a React component.

- [ ] **Step 1: Implement the component**

Create `frontend/src/components/MicButton.tsx`:

```tsx
import type { AssistantState } from '../types';

interface MicButtonProps {
  state: AssistantState;
  onClick: () => void;
}

const ICONS: Record<AssistantState, string> = {
  idle: '🎤',
  recording: '🔴',
  thinking: '⏳',
  speaking: '🔊',
};

export function MicButton({ state, onClick }: MicButtonProps) {
  const disabled = state !== 'idle';

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label="Toggle voice recording"
      className={`relative flex h-20 w-20 items-center justify-center rounded-full text-3xl text-white transition-colors ${
        state === 'recording' ? 'bg-red-500' : 'bg-slate-700'
      } ${disabled ? 'cursor-not-allowed' : 'hover:bg-slate-600'}`}
    >
      {state === 'recording' && (
        <span className="absolute inset-0 animate-ping rounded-full bg-red-400 opacity-75" />
      )}
      {state === 'speaking' && (
        <span className="absolute inset-0 animate-pulse rounded-full bg-blue-400 opacity-50" />
      )}
      <span className="relative">{ICONS[state]}</span>
    </button>
  );
}
```

- [ ] **Step 2: Verify the build compiles**

```bash
cd frontend
npm run build
```
Expected: build completes with no TypeScript errors.

- [ ] **Step 3: Commit**

```bash
cd ..
git add frontend/src/components/MicButton.tsx
git commit -m "Add MicButton component"
```

---

### Task 4: StatusBadge component

**Files:**
- Create: `frontend/src/components/StatusBadge.tsx`

**Interfaces:**
- Consumes: `AssistantState` from `frontend/src/types.ts` (Task 2).
- Produces: `StatusBadge({ state: AssistantState })` — a React component.

- [ ] **Step 1: Implement the component**

Create `frontend/src/components/StatusBadge.tsx`:

```tsx
import type { AssistantState } from '../types';

const LABELS: Partial<Record<AssistantState, string>> = {
  recording: 'Listening…',
  thinking: 'Thinking…',
  speaking: 'Speaking…',
};

export function StatusBadge({ state }: { state: AssistantState }) {
  const label = LABELS[state];
  if (!label) return null;

  return <p className="animate-pulse text-sm font-medium text-slate-500">{label}</p>;
}
```

- [ ] **Step 2: Verify the build compiles**

```bash
cd frontend
npm run build
```
Expected: build completes with no TypeScript errors.

- [ ] **Step 3: Commit**

```bash
cd ..
git add frontend/src/components/StatusBadge.tsx
git commit -m "Add StatusBadge component"
```

---

### Task 5: ChatPanel component

**Files:**
- Create: `frontend/src/components/ChatPanel.tsx`

**Interfaces:**
- Consumes: `ChatMessage` from `frontend/src/types.ts` (Task 2).
- Produces: `ChatPanel({ messages: ChatMessage[] })` — a React component.

- [ ] **Step 1: Implement the component**

Create `frontend/src/components/ChatPanel.tsx`:

```tsx
import type { ChatMessage } from '../types';

export function ChatPanel({ messages }: { messages: ChatMessage[] }) {
  if (messages.length === 0) {
    return (
      <p className="text-center text-sm text-slate-400">
        Press the mic button and ask where to go tonight.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
            message.role === 'user'
              ? 'self-end bg-blue-500 text-white'
              : 'self-start bg-slate-100 text-slate-800'
          }`}
        >
          {message.text}
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Verify the build compiles**

```bash
cd frontend
npm run build
```
Expected: build completes with no TypeScript errors.

- [ ] **Step 3: Commit**

```bash
cd ..
git add frontend/src/components/ChatPanel.tsx
git commit -m "Add ChatPanel component"
```

---

### Task 6: Wire up App.tsx and manually verify the full flow

**Files:**
- Modify: `frontend/src/App.tsx` (full replace)
- Modify: `frontend/src/App.css` (delete — unused after replace)

**Interfaces:**
- Consumes: `useVoiceAssistant` (Task 2), `MicButton` (Task 3), `StatusBadge` (Task 4), `ChatPanel` (Task 5).
- Produces: the composed page rendered at `/`.

- [ ] **Step 1: Remove the unused scaffold stylesheet**

```bash
cd frontend
rm -f src/App.css
```

- [ ] **Step 2: Replace App.tsx**

Replace the entire contents of `frontend/src/App.tsx` with:

```tsx
import { ChatPanel } from './components/ChatPanel';
import { MicButton } from './components/MicButton';
import { StatusBadge } from './components/StatusBadge';
import { useVoiceAssistant } from './hooks/useVoiceAssistant';

function App() {
  const { state, messages, start } = useVoiceAssistant();

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col items-center gap-6 px-4 py-10">
      <h1 className="text-xl font-semibold text-slate-800">Voice Assistant</h1>
      <MicButton state={state} onClick={start} />
      <StatusBadge state={state} />
      <div className="w-full flex-1 overflow-y-auto">
        <ChatPanel messages={messages} />
      </div>
    </div>
  );
}

export default App;
```

- [ ] **Step 3: Verify the build compiles**

```bash
npm run build
```
Expected: build completes with no TypeScript errors, no references to the deleted `App.css`.

- [ ] **Step 4: Manually verify the full fake flow in the browser**

```bash
npm run dev
```
Open the printed local URL (e.g. `http://localhost:5173`) in a browser and confirm, in order:
1. Page shows "Voice Assistant" heading, an idle mic button (🎤), no status text, and the placeholder "Press the mic button…" line.
2. Click the mic button. It turns into a pulsing red circle (🔴) and becomes disabled; status text shows "Listening…".
3. After ~2s, the button shows an hourglass (⏳); status text shows "Thinking…".
4. After ~1.5s more, two chat bubbles appear (user message right-aligned in blue, assistant reply left-aligned in gray) and the button shows a speaker (🔊) with a pulsing blue ring; status text shows "Speaking…".
5. After ~2s more, the button returns to idle (🎤), status text disappears, and the button is clickable again.

Stop the dev server (Ctrl+C) once confirmed.

- [ ] **Step 5: Commit**

```bash
cd ..
git add frontend/src/App.tsx frontend/src/App.css
git commit -m "Wire up App.tsx with the fake voice-assistant flow"
```

---

### Task 7: Deploy to Vercel

**Files:**
- None (platform configuration only; Vite + React needs no `vercel.json`).

**Interfaces:**
- Consumes: the built `frontend/` app from Tasks 1–6.
- Produces: a live Vercel deployment URL reachable by the whole team.

- [ ] **Step 1: Confirm with the user before deploying**

This creates a live, team-visible deployment. Before running anything, confirm with the user which Vercel account/team to deploy under and that they want to proceed now.

- [ ] **Step 2: Link the frontend directory to a Vercel project**

```bash
cd frontend
vercel link
```
Follow the prompts: select the correct scope/team, confirm project name (default `frontend` or rename to match the repo), and confirm `frontend/` as the directory.

- [ ] **Step 3: Set the framework preset and root directory (if not auto-detected)**

In the Vercel project dashboard (Settings → General), confirm:
- Framework Preset: `Vite`
- Root Directory: `frontend`
- Build Command: `npm run build` (default)
- Output Directory: `dist` (default)

- [ ] **Step 4: Deploy to production**

```bash
vercel --prod
```
Expected: CLI prints a production deployment URL.

- [ ] **Step 5: Verify the deployment**

Open the printed production URL in a browser and repeat the manual verification checklist from Task 6, Step 4 (idle → recording → thinking → speaking → idle, chat bubbles appear).

- [ ] **Step 6: Share the URL**

Share the production URL with the team (Kenzhe, Kassiyet, Madina) so they can test it.

- [ ] **Step 7: Commit any Vercel-generated local config**

```bash
cd ..
git status
```
If `vercel link` created a `frontend/.vercel/` directory, ensure it is git-ignored (Vite's default `.gitignore` in `frontend/` should already exclude `.vercel`; if not, add it) rather than committed, since it contains local project linkage, not shareable config.

---

## Self-Review Notes

- **Spec coverage:** stack (Task 1), state machine + timings + fake exchange (Task 2), MicButton visuals (Task 3), StatusBadge (Task 4), ChatPanel/text-duplicate requirement (Task 5), composed layout + manual verification (Task 6), Vercel deployment (Task 7). All spec sections have a corresponding task.
- **No automated tests:** intentional per spec's approved "Testing / verification" section; `npm run build` substitutes as the per-task correctness check, plus explicit manual browser checklists.
- **Type consistency:** `AssistantState` and `ChatMessage` defined once in Task 2 and imported identically (`import type { ... } from '../types'`) in Tasks 3–6; `useVoiceAssistant()` return shape (`state`, `messages`, `start`) matches its usage in Task 6 exactly.
