const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://localhost:8000';

export interface VoiceReply {
  transcript: string;
  replyText: string;
  audioBlob: Blob;
}

export async function sendVoiceMessage(audioBlob: Blob): Promise<VoiceReply> {
  const formData = new FormData();
  formData.append('file', audioBlob, 'recording.webm');

  const response = await fetch(`${BACKEND_URL}/api/chat/audio`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Backend responded with ${response.status}`);
  }

  const transcript = decodeURIComponent(response.headers.get('X-Transcript') ?? '');
  const replyText = decodeURIComponent(response.headers.get('X-Agent-Reply') ?? '');
  const audioBlobOut = await response.blob();

  return { transcript, replyText, audioBlob: audioBlobOut };
}
