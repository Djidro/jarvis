"""The assistant: confirmations first, then commands, then the AI brain."""
import ai_brain, memory
from command_router import route
import permissions


def handle(text):
    text = (text or "").strip()
    if not text:
        return "I didn't catch anything."
    confirmed = permissions.resolve(text)
    memory.add_message("user", text)
    reply = confirmed or route(text) or ai_brain.ask(text)
    memory.add_message("assistant", reply)
    return reply
