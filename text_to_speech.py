"""Offline speech with pyttsx3. Runs in a child process so it can be interrupted instantly."""
import subprocess
import sys

import config

_proc = None
_CODE = "import sys,pyttsx3;e=pyttsx3.init();e.setProperty('rate',175);e.say(sys.argv[1]);e.runAndWait()"


def speak(text):
    global _proc
    stop()
    if config.SPEAK_REPLIES and text:
        _proc = subprocess.Popen([sys.executable, "-c", _CODE, text[:600]])


def stop():
    global _proc
    if _proc and _proc.poll() is None:
        _proc.terminate()
    _proc = None


def is_speaking():
    return _proc is not None and _proc.poll() is None
