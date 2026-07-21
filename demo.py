"""
Quick demo — run this to test TTS without starting the server.
Usage: python demo.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from tts.service import synthesize_to_file, VOICES

SAMPLE_TEXTS = [
    "Сегодня вечером в Алматы есть отличный стендап на улице Абая в 19:00 и джазовый концерт в 20:00. Что предпочитаете?",
    "Tonight in Almaty there's a great stand-up show on Abay street at 19:00 and a jazz concert at 20:00. Which one would you like?",
]

if __name__ == "__main__":
    os.makedirs("demo_output", exist_ok=True)

    for i, text in enumerate(SAMPLE_TEXTS):
        voice = VOICES[i % len(VOICES)]
        output = f"demo_output/sample_{i+1}_{voice}.mp3"
        print(f"[{i+1}] Voice: {voice}")
        print(f"     Text: {text[:60]}...")
        path = synthesize_to_file(text, output, voice=voice)
        print(f"     Saved: {path}\n")

    print("Done! Open demo_output/ to listen.")
