"""Long-term memories and conversation history."""
from database import get_connection


def add_memory(text):
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO memories (text) VALUES (?)", (text,))
        return cur.lastrowid


def list_memories():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, text, created_at FROM memories ORDER BY id").fetchall()
    return [dict(r) for r in rows]


def delete_memory(memory_id):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        return cur.rowcount > 0


def add_message(role, text):
    with get_connection() as conn:
        conn.execute("INSERT INTO messages (role, text) VALUES (?, ?)", (role, text))


def recent_messages(limit=50):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, text FROM messages ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in reversed(rows)]
