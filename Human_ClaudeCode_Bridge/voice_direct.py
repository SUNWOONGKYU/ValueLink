"""
Voice Direct Input for Claude Code
===================================
Win+Shift+H: Start/Stop recording
Recognized text is typed directly into the current window.
"""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.environ['PYTHONUNBUFFERED'] = '1'

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import keyboard
import pyautogui
import pyperclip
import tempfile
import threading
import time
import winsound

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
HOTKEY = "win+shift+h"
LANGUAGE = "ko-KR"

# Global state
recording = False
audio_data = []

def beep(freq=800, duration=100):
    try:
        winsound.Beep(int(freq), int(duration))
    except:
        pass

def safe_print(msg):
    try:
        print(msg, flush=True)
    except:
        print(msg.encode('ascii', 'replace').decode(), flush=True)

def record_audio():
    global recording, audio_data

    audio_data = []
    recording = True

    safe_print("[REC] Recording... (Win+Shift+H to stop)")
    beep(800, 150)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16') as stream:
        while recording:
            data, _ = stream.read(1024)
            audio_data.append(data.copy())

def stop_and_transcribe():
    global recording, audio_data

    if not recording:
        return

    recording = False
    beep(600, 100)
    safe_print("[STOP] Processing...")

    if not audio_data:
        safe_print("[X] No audio")
        return

    audio_np = np.concatenate(audio_data, axis=0)
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    wav.write(temp_file.name, SAMPLE_RATE, audio_np)
    temp_file.close()

    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_file.name) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio, language=LANGUAGE)
        safe_print(f"[OK] {text}")

        old_clip = ""
        try:
            old_clip = pyperclip.paste()
        except:
            pass

        pyperclip.copy(text)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')

        time.sleep(0.2)
        try:
            pyperclip.copy(old_clip)
        except:
            pass

        beep(500, 100)

    except sr.UnknownValueError:
        safe_print("[X] Could not understand")
        beep(300, 300)
    except sr.RequestError as e:
        safe_print(f"[X] API error: {e}")
        beep(300, 300)
    except Exception as e:
        safe_print(f"[X] Error: {e}")
        beep(300, 300)
    finally:
        os.unlink(temp_file.name)

def toggle():
    global recording
    if recording:
        stop_and_transcribe()
    else:
        t = threading.Thread(target=record_audio, daemon=True)
        t.start()

def main():
    safe_print("=" * 50)
    safe_print("  Voice Direct Input")
    safe_print("=" * 50)
    safe_print("")
    safe_print("  Hotkey: WIN + SHIFT + H")
    safe_print("  Language: Korean")
    safe_print("")
    safe_print("  1. Focus Claude Code window")
    safe_print("  2. Win+Shift+H = Start recording")
    safe_print("  3. Speak")
    safe_print("  4. Win+Shift+H = Stop & type")
    safe_print("")
    safe_print("  Ctrl+C to exit")
    safe_print("=" * 50)
    safe_print("")
    safe_print("Ready!")

    beep(800, 100)
    time.sleep(0.05)
    beep(1000, 100)

    keyboard.add_hotkey(HOTKEY, toggle, suppress=True)

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        safe_print("\nBye!")

if __name__ == "__main__":
    main()
