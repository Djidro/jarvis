"""Safe computer actions. Only whitelisted apps and http(s) sites are allowed."""
import os
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus

import config
from permissions import log_action, can_launch_programs


def current_time():
    return datetime.now().strftime("It is %I:%M %p.").replace("It is 0", "It is ")


def current_date():
    return datetime.now().strftime("Today is %A, %B %d, %Y.")


def open_website(name):
    url = config.KNOWN_SITES.get(name.lower())
    if url is None:
        return None
    webbrowser.open(url)
    log_action("open_website", url)
    return f"Opening {name}."


def search_web(query):
    url = "https://www.google.com/search?q=" + quote_plus(query)
    webbrowser.open(url)
    log_action("search_web", query)
    return f"Searching the web for {query}."


def open_app(name):
    program = config.ALLOWED_APPS.get(name.lower())
    if program is None:
        return None
    if not can_launch_programs():
        log_action("blocked_by_safe_mode", name)
        return "Safe mode is on, so I can't launch programs."
    try:
        if hasattr(os, "startfile"):      # Windows
            os.startfile(program)
        else:                             # other systems (development only)
            subprocess.Popen([program])
    except OSError as err:
        log_action("open_app_failed", f"{name}: {err}")
        return f"I couldn't open {name}."
    log_action("open_app", program)
    return f"Opening {name}."


def volume(direction):
    import pyautogui
    key = {"up": "volumeup", "down": "volumedown", "mute": "volumemute"}[direction]
    for _ in range(5 if direction != "mute" else 1):
        pyautogui.press(key)
    log_action("volume", direction)
    return "Volume " + direction + "."


def screenshot():
    import pyautogui
    from pathlib import Path
    folder = Path.home() / "Pictures" / "JARVIS_screenshots"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"shot_{datetime.now():%Y%m%d_%H%M%S}.png"
    pyautogui.screenshot(str(path))
    log_action("screenshot", str(path))
    return f"Screenshot saved to {path}."
