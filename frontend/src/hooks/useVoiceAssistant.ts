import { useCallback, useRef, useState } from 'react';
import type { AssistantState, ChatMessage } from '../types';
import { useMediaRecorder } from './useMediaRecorder';
import { sendVoiceMessage } from '../lib/api';

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
  const recorder = useMediaRecorder();

  const startRecording = useCallback(async () => {
    try {
      await recorder.start();
      setState('recording');
    } catch {
      setState('error');
    }
  }, [recorder]);

  const stopAndSend = useCallback(async () => {
    setState('thinking');
    try {
      const audioBlob = await recorder.stop();
      const { transcript, replyText, audioBlob: replyAudio } = await sendVoiceMessage(audioBlob);

      setMessages((prev) => [
        ...prev,
        { id: `${Date.now()}-user`, role: 'user', text: transcript },
        { id: `${Date.now()}-assistant`, role: 'assistant', text: replyText },
      ]);
      setState('speaking');

      const audioUrl = URL.createObjectURL(replyAudio);
      const audio = new Audio(audioUrl);
      const finish = () => {
        URL.revokeObjectURL(audioUrl);
        setState('idle');
      };
      audio.onended = finish;
      audio.onerror = finish;
      await audio.play();
    } catch {
      setState('error');
    }
  }, [recorder]);

  const start = useCallback(() => {
    const current = stateRef.current;
    if (current === 'idle' || current === 'error') {
      startRecording();
    } else if (current === 'recording') {
      stopAndSend();
    }
  }, [startRecording, stopAndSend]);

  return { state, messages, start };
}
