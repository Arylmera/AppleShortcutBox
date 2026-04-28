#!/usr/bin/env python3
"""
hello-world.py — minimal shortcut that shows a notification and speaks text.

This is the canonical first shortcut; if this round-trips and imports
successfully, the toolchain is working.
"""

from pathlib import Path

from _shortcut_lib import base_workflow, make_action, write_shortcut


REPO_ROOT = Path(__file__).resolve().parent.parent
SLUG = "hello-world"


def build() -> dict:
    actions = [
        make_action(
            "is.workflow.actions.notification",
            {
                "WFNotificationActionTitle": "Hello from code",
                "WFNotificationActionBody": "This shortcut was built in Python.",
            },
        ),
        make_action(
            "is.workflow.actions.speaktext",
            {
                "WFText": "Shortcut built from Python",
            },
        ),
    ]
    return base_workflow(actions)


if __name__ == "__main__":
    write_shortcut(build(), REPO_ROOT / "raw" / f"{SLUG}.shortcut")
