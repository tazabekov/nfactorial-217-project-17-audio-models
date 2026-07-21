export type AssistantState = 'idle' | 'recording' | 'thinking' | 'speaking';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
}
