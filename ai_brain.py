"""General conversation. Tries local Ollama first, then optional cloud."""
import json
import os
import urllib.request

import config
import memory

SYSTEM = ("You are Jarvis, a concise, helpful personal assistant. Be honest: if you are not "
          "sure of something, say so, and never present a guess as a verified fact. "
          "Known facts about the user: {facts}")


def _post(url, payload, headers=None, timeout=120):
    req = urllib.request.Request(url, json.dumps(payload).encode(),
                                 {"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _messages():
    facts = "; ".join(m["text"] for m in memory.list_memories()) or "none"
    msgs = [{"role": "system", "content": SYSTEM.format(facts=facts)}]
    return msgs + memory.recent_messages(12)   # includes the newest user message


def ask(_text=None):
    msgs = _messages()
    try:
        data = _post(config.OLLAMA_URL, {"model": config.OLLAMA_MODEL, "messages": msgs, "stream": False})
        return data["message"]["content"].strip()
    except Exception:
        pass
    key = os.environ.get("JARVIS_CLOUD_KEY")
    if config.CLOUD_URL and key:
        try:
            data = _post(config.CLOUD_URL, {"model": config.CLOUD_MODEL, "messages": msgs},
                         {"Authorization": "Bearer " + key})
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass
    return ("My AI brain is offline. Install Ollama (ollama.com), run "
            f"'ollama pull {config.OLLAMA_MODEL}', and keep it running.")
