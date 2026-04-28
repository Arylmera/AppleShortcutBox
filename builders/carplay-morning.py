#!/usr/bin/env python3
"""
carplay-morning.py — open Waze and start Spotify Liked Songs, but only
before 07:00. Intended to be triggered by an iOS personal automation
(Shortcuts → Automation → CarPlay → Connects → Run Shortcut).

Built on top of python-shortcuts via `_shortcut_lib`.
The If's input is implicit — it tests the *previous* action's output.
That's why Format Date sits directly above the If: the If reads the
formatted hour string ("0".."23") and compares it numerically to "7".

URL schemes:
    waze://                     opens Waze
    spotify:collection:tracks   opens Spotify Liked Songs view
                                (Spotify must be installed and signed in)
"""

from pathlib import Path

from _shortcut_lib import (
    DateAction,
    EndIfAction,
    FormatDateAction,
    IfActionExt,
    OpenURLAction,
    URLAction,
    write_shortcut,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
SLUG = "carplay-morning"


def build():
    return [
        # Get current date.
        DateAction(),
        # Format it as 24h hour-of-day, e.g. "5". This becomes the
        # implicit input to the If below.
        FormatDateAction({"format": "H"}),
        # If hour < 7 ...
        # Numeric conditions use WFNumberValue (compare_with_number),
        # NOT WFConditionalActionString (compare_with). Verified via cherri.
        IfActionExt({"condition": "Is Less Than", "compare_with_number": 7}),
        # Open Waze.
        URLAction({"url": "waze://"}),
        OpenURLAction(),
        # Open Spotify Liked Songs.
        URLAction({"url": "spotify:collection:tracks"}),
        OpenURLAction(),
        # End If.
        EndIfAction(),
    ]


if __name__ == "__main__":
    write_shortcut(build(), REPO_ROOT / "raw" / f"{SLUG}.shortcut")
