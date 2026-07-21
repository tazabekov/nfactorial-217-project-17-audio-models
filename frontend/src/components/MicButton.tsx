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
