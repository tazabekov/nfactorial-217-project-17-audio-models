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
