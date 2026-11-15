"""Action logging, safe mode, and yes/no confirmation for risky actions."""
from datetime import datetime
import config

_pending = None   # (prompt, function)


def log_action(action, detail=""):
    config.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(config.LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {action} | {detail}\n")


def can_launch_programs():
    return not config.SAFE_MODE


def ask(prompt, func):
    """Store a risky action; it only runs if the user says yes next."""
    global _pending
    _pending = (prompt, func)
    return prompt + " Say 'yes' to confirm or 'no' to cancel."


def resolve(text):
    """Returns a reply if a confirmation was pending, else None."""
    global _pending
    if _pending is None:
        return None
    word = text.strip().lower().rstrip(".! ")
    func = _pending[1]
    if word in ("yes", "confirm", "yes please", "do it"):
        _pending = None
        log_action("confirmed", "")
        return func()
    if word in ("no", "cancel", "stop", "no thanks"):
        _pending = None
        return "Cancelled."
    return None
