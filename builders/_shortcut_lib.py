"""
_shortcut_lib.py — thin wrapper around python-shortcuts for this repo.

We adopted python-shortcuts (https://github.com/alexander-akhmetov/python-shortcuts)
on 2026-04-28 as the engine for emitting valid binary-plist `.shortcut` files.
This module:

  1. Re-exports the action classes we use, so builders import from one place.
  2. Adds extensions where the upstream library is incomplete (notably the If
     action, which only exposes Equals/Contains in its enum but iOS supports
     a full set of operators — see CONDITION_OPERATORS below).
  3. Provides a `write_shortcut(actions, path)` helper that wraps the
     Shortcut/dump/round-trip-check boilerplate.

If you need an action that python-shortcuts does not expose:
  - First check `docs/external-libraries.md` to see if the schema is
    cross-referenced.
  - Subclass `BaseAction` here (see `IfActionExt` for a model).
  - Add an entry to `docs/action-reference.md`.

Install: `pip3 install --user shortcuts`
"""

from __future__ import annotations

import plistlib
from pathlib import Path

# python-shortcuts 0.11.0 still uses `plistlib.Data`, which Python removed in
# 3.9 (deprecated since 3.4). For our purposes raw `bytes` is a drop-in
# replacement, so we shim it back before importing from `shortcuts`.
if not hasattr(plistlib, "Data"):
    plistlib.Data = lambda data: data  # type: ignore[attr-defined]

from shortcuts import FMT_SHORTCUT, Shortcut
from shortcuts.actions.base import (
    BaseAction,
    ChoiceField,
    GroupIDField,
    IntegerField,
    VariablesField,
)

# Re-export the upstream action classes that builders use directly.
from shortcuts.actions import (  # noqa: F401
    DateAction,
    ElseAction,
    EndIfAction,
    FormatDateAction,
    NotificationAction,
    OpenAppAction,
    OpenURLAction,
    SpeakTextAction,
    URLAction,
)


# ---------------------------------------------------------------------------
# Extended If action — full operator set
# ---------------------------------------------------------------------------

# Cross-referenced from drewburchfield/shortcuts-toolkit (action-library.js:343).
# These are STRINGS in the plist, not integer codes.
CONDITION_OPERATORS = (
    "Equals",
    "Contains",
    "Is Greater Than",
    "Is Less Than",
    "Begins With",
    "Ends With",
    "Has Any Value",
    "Does Not Have Any Value",
)


class IfActionExt(BaseAction):
    """If action with the full WFCondition operator set.

    Upstream's `IfAction` only exposes Equals/Contains and only emits the
    string-comparison field `WFConditionalActionString`. This subclass adds:

      - The full operator enum (see `CONDITION_OPERATORS`).
      - `compare_with_number` → `WFNumberValue`, the field iOS expects when
        the operator is numeric ("Is Less Than", "Is Greater Than", "Equals"
        on numbers). String operators ("Contains", "Begins With", …) keep
        using `compare_with` → `WFConditionalActionString`.

    Pick whichever field matches your operator. Verified via the cherri
    compiler's source (electrikmilk/cherri, shortcutgen.go:960-966).

    The If's input is implicit — it operates on the previous action's
    output. Insert a Set Variable upstream if you need to test something
    other than the immediately-prior result.
    """

    itype = "is.workflow.actions.conditional"
    keyword = "if_ext"

    _additional_identifier_field = "WFControlFlowMode"

    condition = ChoiceField(
        "WFCondition",
        choices=CONDITION_OPERATORS,
        default="Equals",
    )
    compare_with = VariablesField("WFConditionalActionString", required=False)
    compare_with_number = IntegerField("WFNumberValue", required=False)
    group_id = GroupIDField("GroupingIdentifier")

    default_fields = {"WFControlFlowMode": 0}


# ---------------------------------------------------------------------------
# Output helper
# ---------------------------------------------------------------------------


def write_shortcut(actions: list[BaseAction], out_path: str | Path) -> Path:
    """Build a Shortcut from `actions` and write it to `out_path` as binary plist.

    Round-trips through plistlib to confirm the file is well-formed before
    returning. Prints a one-line confirmation.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    sc = Shortcut(actions=actions)
    with out.open("wb") as f:
        sc.dump(f, file_format=FMT_SHORTCUT)

    with out.open("rb") as f:
        parsed = plistlib.load(f)
    assert len(parsed["WFWorkflowActions"]) == len(actions), (
        "Round-trip action count mismatch — plist is malformed"
    )

    n = len(actions)
    print(f"Wrote {out} ({n} action{'s' if n != 1 else ''})")
    return out
