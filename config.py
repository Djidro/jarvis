"""Central settings for JARVIS. Edit values here, not in other files."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "jarvis.db"
LOG_PATH = BASE_DIR / "actions.log"

HOST = "127.0.0.1"   # localhost only: nobody else on your network can reach it
PORT = 5000

ASSISTANT_NAME = "Jarvis"

# Safe mode blocks anything that launches programs. Websites and notes still work.
SAFE_MODE = False

# Only programs on this list can ever be launched. Add your own: "name": "program.exe"
ALLOWED_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe",
}

# Websites you can open by name.
KNOWN_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "wikipedia": "https://www.wikipedia.org",
}

# ---- AI brain ----
# Local (free): install Ollama from ollama.com, then run:  ollama pull qwen2.5:1.5b
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:1.5b"
# Optional cloud (any OpenAI-compatible API). The key is read from the environment
# variable JARVIS_CLOUD_KEY and never sent to the browser. Leave CLOUD_URL empty to disable.
CLOUD_URL = ""   # e.g. "https://api.openai.com/v1/chat/completions"
CLOUD_MODEL = ""

# ---- Voice ----
VOSK_MODEL_PATH = BASE_DIR / "vosk-model-small-en-us-0.15"
WAKE_WORD = "jarvis"
SPEAK_REPLIES = True
