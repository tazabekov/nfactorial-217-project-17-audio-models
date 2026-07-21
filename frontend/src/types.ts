export type AssistantState = 'idle' | 'recording' | 'thinking' | 'speaking' | 'error';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
}
