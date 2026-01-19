"""
Voice Realtime Input - 시작하면 계속 듣기
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import sounddevice as sd
import numpy as np
import requests
import json
import pyperclip
import pyautogui
import time
import winsound
import threading
import queue

LANGUAGE = "ko-KR"
SAMPLE_RATE = 16000

audio_queue = queue.Queue()

def beep(freq=800, duration=100):
    try:
        winsound.Beep(int(freq), int(duration))
    except:
        pass

def type_text(text):
    if not text.strip():
        return
    old = ""
    try:
        old = pyperclip.paste()
    except:
        pass
    pyperclip.copy(text + " ")
    time.sleep(0.03)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.05)
    try:
        pyperclip.copy(old)
    except:
        pass

def audio_to_wav_bytes(audio_data, sample_rate):
    import io
    import wave
    audio_int16 = (audio_data * 32767).astype(np.int16)
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    return buffer.getvalue()

def recognize_google(audio_bytes, language="ko-KR"):
    url = "http://www.google.com/speech-api/v2/recognize"
    params = {"client": "chromium", "lang": language, "key": "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"}
    headers = {"Content-Type": "audio/l16; rate=16000"}
    try:
        response = requests.post(url, params=params, headers=headers, data=audio_bytes, timeout=3)
        for line in response.text.strip().split('\n'):
            if line:
                result = json.loads(line)
                if 'result' in result and result['result']:
                    if result['result'][0].get('alternative'):
                        return result['result'][0]['alternative'][0]['transcript']
    except:
        pass
    return None

def process_audio():
    buffer = []
    silence_count = 0
    is_speaking = False

    while True:
        try:
            data = audio_queue.get(timeout=0.1)
            volume = np.abs(data).mean()

            if volume > 0.01:
                buffer.append(data)
                silence_count = 0
                is_speaking = True
            elif is_speaking:
                buffer.append(data)
                silence_count += 1

                if silence_count > 2:
                    if len(buffer) > 3:
                        audio = np.concatenate(buffer)
                        wav_bytes = audio_to_wav_bytes(audio, SAMPLE_RATE)
                        text = recognize_google(wav_bytes, LANGUAGE)
                        if text:
                            print(f">> {text}", flush=True)
                            type_text(text)
                            beep(500, 30)
                    buffer = []
                    silence_count = 0
                    is_speaking = False
        except queue.Empty:
            pass

def audio_callback(indata, frames, time_info, status):
    audio_queue.put(indata[:, 0].copy())

def main():
    print("Voice Input ON", flush=True)
    beep(800, 100)
    beep(1000, 100)

    proc_thread = threading.Thread(target=process_audio, daemon=True)
    proc_thread.start()

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback, blocksize=1024):
        while True:
            sd.sleep(1000)

if __name__ == "__main__":
    main()
