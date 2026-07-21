import { useCallback, useRef, useState } from 'react';
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
  const stateRef = useRef<AssistantState>(state);
  stateRef.current = state;

  const start = useCallback(() => {
    if (stateRef.current !== 'idle') return;

    setState('recording');

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
  }, []);

  return { state, messages, start };
}
