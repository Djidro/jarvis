"""Offline microphone listening (Vosk). Waits for the wake word, then takes one command."""
import json
import queue
import threading

import config

_thread = None
_running = False
state = {"mic_on": False, "heard": "", "error": ""}


def start(on_command):
    global _thread, _running
    if _running:
        return True
    if not config.VOSK_MODEL_PATH.exists():
        state["error"] = "Vosk model not found in models/. See README step 5."
        return False
    state["error"] = ""
    _running = True
    _thread = threading.Thread(target=_loop, args=(on_command,), daemon=True)
    _thread.start()
    return True


def stop():
    global _running
    _running = False
    state["mic_on"] = False


def _loop(on_command):
    global _running
    try:
        import sounddevice as sd
        from vosk import Model, KaldiRecognizer
        import text_to_speech as tts
        rec = KaldiRecognizer(Model(str(config.VOSK_MODEL_PATH)), 16000)
        audio = queue.Queue()
        awake = False
        with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype="int16", channels=1,
                               callback=lambda d, f, t, s: audio.put(bytes(d))):
            state["mic_on"] = True
            while _running:
                if not rec.AcceptWaveform(audio.get()):
                    continue
                text = json.loads(rec.Result()).get("text", "").strip()
                if not text:
                    continue
                if tts.is_speaking() and text in ("stop", "jarvis stop"):
                    tts.stop()          # interrupt speech by voice
                    continue
                if not awake and config.WAKE_WORD in text:
                    text = text.split(config.WAKE_WORD, 1)[1].strip()
                    awake = True
                if awake and text:
                    state["heard"] = text
                    awake = False
                    on_command(text)
                # if only the wake word was said, stay awake for the next phrase
    except Exception as err:
        state["error"] = str(err)
    finally:
        _running = False
        state["mic_on"] = False
