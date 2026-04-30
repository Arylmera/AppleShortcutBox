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
    NumberCoerceAction,
    OpenURLAction,
    SetVariableAction,
    URLAction,
    write_shortcut,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
SLUG = "carplay-morning"


def build():
    return [
        # Get current date.
        DateAction(),
        # Format as 24h hour-of-day → string like "5" or "10".
        FormatDateAction({"format": "H"}),
        # Save into a named variable so we can pass it as a magic-var
        # reference into the next action.
        SetVariableAction({"name": "Hour"}),
        # Coerce to a Number-typed value. Without this, the If below
        # does LEXICOGRAPHIC comparison ("10" < "7" because '1' < '7'
        # as characters) and fires the body all day except at 7/8/9.
        NumberCoerceAction({"number": "{{Hour}}"}),
        # If hour < 7 ...
        # Numeric conditions use WFNumberValue (compare_with_number),
        # NOT WFConditionalActionString (compare_with). Verified via cherri.
        IfActionExt({"condition": "Is Less Than", "compare_with_number": 7}),
        # Start Spotify Liked Songs first so music is already playing
        # before we hand the foreground to Waze.
        URLAction({"url": "spotify:collection:tracks"}),
        OpenURLAction(),
        # Then open Waze for navigation/traffic.
        URLAction({"url": "waze://"}),
        OpenURLAction(),
        # End If.
        EndIfAction(),
    ]


if __name__ == "__main__":
    write_shortcut(build(), REPO_ROOT / "raw" / f"{SLUG}.shortcut")
