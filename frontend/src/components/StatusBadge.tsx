import type { AssistantState } from '../types';

const LABELS: Partial<Record<AssistantState, string>> = {
  recording: 'Listening…',
  thinking: 'Thinking…',
  speaking: 'Speaking…',
  error: 'Something went wrong — tap to retry.',
};

export function StatusBadge({ state }: { state: AssistantState }) {
  const label = LABELS[state];
  if (!label) return null;

  const colorClass = state === 'error' ? 'text-red-500' : 'text-slate-500';

  return <p className={`animate-pulse text-sm font-medium ${colorClass}`}>{label}</p>;
}
