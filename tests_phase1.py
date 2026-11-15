"""Run: python tests_phase1.py   (uses a temporary database, never your real one)"""
import tempfile, pathlib
import config
config.SPEAK_REPLIES = False
config.DB_PATH = pathlib.Path(tempfile.mkdtemp()) / "test.db"
config.LOG_PATH = pathlib.Path(tempfile.mkdtemp()) / "test.log"

from database import init_db
import assistant, memory
import main

init_db()
c = main.app.test_client()
def ask(t): return c.post("/api/chat", json={"text": t}).get_json()["reply"]

assert "It is" in ask("what time is it")
assert "Today is" in ask("what's the date")
assert "remember" in ask("remember that I like tea").lower()
assert len(memory.list_memories()) == 1
assert "tea" in ask("what do you remember")
assert ask("forget 1") == "Memory deleted."
assert memory.list_memories() == []
assert ask("open youtube") == "Opening youtube."
assert "don't know" in ask("open malware.exe")
assert "AI brain is offline" in ask("blah blah")  # no Ollama in test environment
config.SAFE_MODE = True
assert "Safe mode" in ask("open notepad")
assert c.get("/").status_code == 200
assert c.get("/static/script.js").status_code == 200
print("All Phase 1 tests passed.")

# ---- extra features ----
import productivity
assert ask("note: buy milk") == "Note saved."
assert "buy milk" in ask("show notes")
assert ask("task: call mom") == "Task added."
assert "call mom" in ask("show tasks")
assert ask("complete task 1") == "Task completed."
assert "Timer set" in ask("set a timer for 1 second")
import time; time.sleep(1.5); assert productivity.pop_alerts() == ["Your timer is done."]
assert "open tasks" in ask("daily report")
import tempfile, os
f = pathlib.Path.home() / "jarvis_test_delete.txt"; f.write_text("x")
assert "permanently delete" in ask(f"delete file {f}")
assert ask("no") == "Cancelled." and f.exists()
ask(f"delete file {f}"); assert ask("yes") == "File deleted." and not f.exists()
assert "home folder" in ask("delete file /etc/passwd")
print("All extra-feature tests passed.")
