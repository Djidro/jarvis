"""Starts JARVIS: python main.py"""
import threading
import webbrowser

from flask import Flask, abort, jsonify, request, send_from_directory

import config
import assistant, memory, productivity
import listener, text_to_speech as tts
from database import init_db

app = Flask(__name__, static_folder=None)
INTERFACE = config.BASE_DIR
PUBLIC_FILES = {"style.css", "script.js"}   # only these are ever sent to the browser


@app.route("/")
def index():
    return send_from_directory(INTERFACE, "index.html")


@app.route("/static/<name>")
def public_file(name):
    if name not in PUBLIC_FILES:
        abort(404)
    return send_from_directory(INTERFACE, name)


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    reply = assistant.handle(data.get("text", ""))
    tts.speak(reply)
    return jsonify(reply=reply)


@app.get("/api/history")
def history():
    return jsonify(memory.recent_messages())


@app.get("/api/memories")
def memories():
    return jsonify(memory.list_memories())


@app.delete("/api/memories/<int:memory_id>")
def delete_memory(memory_id):
    return jsonify(deleted=memory.delete_memory(memory_id))


@app.get("/api/status")
def status():
    return jsonify(name=config.ASSISTANT_NAME, safe_mode=config.SAFE_MODE, microphone=listener.state["mic_on"], mic_error=listener.state["error"])


def _voice_command(text):
    reply = assistant.handle(text)
    productivity.ALERTS.append("You: " + text + "\nJarvis: " + reply)
    tts.speak(reply)


@app.post("/api/mic")
def mic():
    if request.get_json(silent=True, force=True).get("on"):
        listener.start(_voice_command)
    else:
        listener.stop()
    return jsonify(ok=True)


@app.post("/api/stop")
def stop_speaking():
    tts.stop()
    return jsonify(ok=True)


@app.get("/api/alerts")
def alerts():
    return jsonify(productivity.pop_alerts())


if __name__ == "__main__":
    init_db()
    url = f"http://{config.HOST}:{config.PORT}"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print(f"JARVIS running at {url}  (press Ctrl+C to stop)")
    app.run(host=config.HOST, port=config.PORT, debug=False)
