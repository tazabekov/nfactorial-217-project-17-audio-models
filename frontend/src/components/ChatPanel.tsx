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
