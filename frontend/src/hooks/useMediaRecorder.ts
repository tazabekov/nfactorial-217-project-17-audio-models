import { useCallback, useRef } from 'react';

interface UseMediaRecorderResult {
  start: () => Promise<void>;
  stop: () => Promise<Blob>;
}

export function useMediaRecorder(): UseMediaRecorderResult {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  const start = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;
    chunksRef.current = [];

    const recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };
    recorderRef.current = recorder;
    recorder.start();
  }, []);

  const stop = useCallback((): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      const recorder = recorderRef.current;
      if (!recorder) {
        reject(new Error('No active recording'));
        return;
      }

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType });
        streamRef.current?.getTracks().forEach((track) => track.stop());
        resolve(blob);
      };
      recorder.stop();
    });
  }, []);

  return { start, stop };
}
