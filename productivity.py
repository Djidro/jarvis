"""Notes, tasks, timers, reminders and the daily report."""
import threading
from datetime import datetime
from database import get_connection

ALERTS = []   # messages waiting for the interface to pick up


def _add(table, text):
    with get_connection() as c:
        return c.execute(f"INSERT INTO {table} (text) VALUES (?)", (text,)).lastrowid


def add_note(text): return _add("notes", text)
def add_task(text): return _add("tasks", text)


def list_notes():
    with get_connection() as c:
        return [dict(r) for r in c.execute("SELECT id, text FROM notes ORDER BY id")]


def list_tasks(only_open=True):
    q = "SELECT id, text, done FROM tasks" + (" WHERE done = 0" if only_open else "") + " ORDER BY id"
    with get_connection() as c:
        return [dict(r) for r in c.execute(q)]


def finish_task(task_id):
    with get_connection() as c:
        return c.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,)).rowcount > 0


def set_timer(seconds, message):
    t = threading.Timer(seconds, lambda: ALERTS.append(message))
    t.daemon = True
    t.start()


def pop_alerts():
    out = ALERTS[:]
    ALERTS.clear()
    return out


def daily_report():
    tasks, notes = list_tasks(), list_notes()
    text = f"{datetime.now():%A, %B %d}. You have {len(tasks)} open tasks and {len(notes)} notes."
    if tasks:
        text += " Open tasks: " + "; ".join(f"#{t['id']} {t['text']}" for t in tasks) + "."
    return text
