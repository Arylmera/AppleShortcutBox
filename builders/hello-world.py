#!/usr/bin/env python3
"""
hello-world.py — minimal shortcut: notification + speak text.

Toolchain smoke test. If this round-trips and imports cleanly, the
python-shortcuts wiring in `_shortcut_lib.py` is healthy.
"""

from pathlib import Path

from _shortcut_lib import NotificationAction, SpeakTextAction, write_shortcut


REPO_ROOT = Path(__file__).resolve().parent.parent
SLUG = "hello-world"


def build():
    return [
        NotificationAction({
            "title": "Hello from code",
            "text": "This shortcut was built in Python.",
        }),
        # SpeakTextAction in python-shortcuts has no `text` field — it speaks
        # the previous action's output. The notification body above is what
        # gets spoken.
        SpeakTextAction({
            "language": "English (United States)",
            "rate": 0.44,
            "pitch": 0.95,
            "wait_until_finished": True,
        }),
    ]


if __name__ == "__main__":
    write_shortcut(build(), REPO_ROOT / "raw" / f"{SLUG}.shortcut")
