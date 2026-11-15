"""Turns a sentence into an action. Returns a reply, or None if no command matched."""
import json
import re
import urllib.parse
import urllib.request

import computer_control as pc, file_manager as fm
import memory, productivity as prod
import permissions


def _seconds(amount, unit):
    return int(amount) * {"s": 1, "m": 60, "h": 3600}[unit[0]]


def _lookup(query):
    url = "https://api.duckduckgo.com/?format=json&no_html=1&q=" + urllib.parse.quote_plus(query)
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
    except Exception:
        return "I couldn't reach the internet."
    if data.get("AbstractText"):
        return f"According to {data.get('AbstractSource', 'DuckDuckGo')} (not verified by me): {data['AbstractText']}"
    return "I found no reliable summary for that. I can open a web search instead: say 'search for ...'."


def route(text):
    t = text.strip()
    low = t.lower().rstrip("?.! ")

    if re.search(r"\btime\b", low) and len(low.split()) <= 6: return pc.current_time()
    if re.search(r"\b(date|what day)\b", low) and len(low.split()) <= 6: return pc.current_date()

    m = re.match(r"(?:please )?remember(?: that)? (.+)", t, re.I)
    if m:
        memory.add_memory(m.group(1).strip()); return "Noted. I will remember that."
    if low in ("what do you remember", "list memories", "show memories"):
        items = memory.list_memories()
        return "I remember: " + "; ".join(f"#{i['id']} {i['text']}" for i in items) if items else "I have no saved memories yet."
    m = re.match(r"forget (?:memory )?#?(\d+)", low)
    if m:
        return "Memory deleted." if memory.delete_memory(int(m.group(1))) else "I couldn't find that memory."

    m = re.match(r"(?:add )?note[: ]+(.+)", t, re.I) or re.match(r"take a note[: ]+(.+)", t, re.I)
    if m:
        prod.add_note(m.group(1)); return "Note saved."
    if low in ("show notes", "list notes", "my notes"):
        n = prod.list_notes()
        return "Notes: " + "; ".join(f"#{x['id']} {x['text']}" for x in n) if n else "No notes yet."
    m = re.match(r"(?:add )?task[: ]+(.+)", t, re.I)
    if m:
        prod.add_task(m.group(1)); return "Task added."
    if low in ("show tasks", "list tasks", "my tasks"):
        n = prod.list_tasks()
        return "Tasks: " + "; ".join(f"#{x['id']} {x['text']}" for x in n) if n else "No open tasks."
    m = re.match(r"(?:complete|finish|done) task #?(\d+)", low)
    if m:
        return "Task completed." if prod.finish_task(int(m.group(1))) else "I couldn't find that task."
    if "daily report" in low or "daily summary" in low: return prod.daily_report()

    m = re.search(r"(?:set (?:a )?(?:timer|alarm) for|remind me in) (\d+) ?(second|minute|hour|sec|min|hr)s?(?: to (.+))?", low)
    if m:
        secs = _seconds(m.group(1), m.group(2)[0] if m.group(2) != "hr" else "h")
        msg = f"Reminder: {m.group(3)}" if m.group(3) else "Your timer is done."
        prod.set_timer(secs, msg); permissions.log_action("timer", f"{secs}s")
        return f"Timer set for {m.group(1)} {m.group(2)}s."

    m = re.match(r"volume (up|down)|turn (?:the )?volume (up|down)|(mute)", low)
    if m:
        try: return pc.volume(next(g for g in m.groups() if g))
        except Exception as e: return f"I couldn't change the volume: {e}"
    if "screenshot" in low:
        try: return pc.screenshot()
        except Exception as e: return f"I couldn't take a screenshot: {e}"

    m = re.match(r"(?:find|search) files? (?:named |called )?(.+)", t, re.I)
    if m:
        r = fm.search_files(m.group(1).strip())
        return "Found: " + "; ".join(r) if r else "I found no matching files in Documents, Downloads, Desktop or Pictures."
    m = re.match(r"delete file (.+)", t, re.I)
    if m:
        path = m.group(1).strip().strip('"')
        if not fm.is_safe_to_delete(path):
            return "I only delete existing files inside your home folder."
        return permissions.ask(f"I am about to permanently delete {path}.",
                               lambda: (permissions.log_action("delete_file", path), fm.delete_file(path))[1])

    m = re.match(r"(?:look up|what is|who is|tell me about) (.+)", t, re.I)
    if m and low.startswith(("look up", "search the internet")): return _lookup(m.group(1))
    m = re.match(r"(?:search(?: the web)? for|google) (.+)", t, re.I)
    if m: return pc.search_web(m.group(1).strip())

    m = re.match(r"open (.+)", low)
    if m:
        target = m.group(1).strip()
        try: reply = pc.open_website(target) or pc.open_app(target) or fm.open_folder(target)
        except Exception as e: return f"I couldn't open {target}: {e}"
        return reply or f"I don't know how to open {target} yet."
    return None
