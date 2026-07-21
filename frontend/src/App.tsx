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
