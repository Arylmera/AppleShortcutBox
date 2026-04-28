"""
_shortcut_lib.py — shared helpers for building Apple .shortcut files.

Every builder in this folder imports from this module. If you find yourself
copying boilerplate, ADD a helper here instead. See docs/SKILL.md for the
contract.
"""

from __future__ import annotations

import plistlib
import uuid
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# UUIDs and action construction
# ---------------------------------------------------------------------------


def new_uuid() -> str:
    """Generate a fresh UUID in the uppercase hyphenated form Apple uses."""
    return str(uuid.uuid4()).upper()


def make_action(
    identifier: str,
    params: dict[str, Any] | None = None,
    *,
    uuid_str: str | None = None,
) -> dict[str, Any]:
    """Build one WFWorkflowAction dict.

    Args:
        identifier: e.g. "is.workflow.actions.notification"
        params: parameter dict for this action; UUID will be added if missing
        uuid_str: pass a specific UUID if another action needs to reference
                  this one. If None, a fresh UUID is generated.

    Returns:
        A dict with keys WFWorkflowActionIdentifier and WFWorkflowActionParameters.
        The UUID is also stored under params["UUID"] so callers can reference it.
    """
    p = dict(params or {})
    p.setdefault("UUID", uuid_str or new_uuid())
    return {
        "WFWorkflowActionIdentifier": identifier,
        "WFWorkflowActionParameters": p,
    }


# ---------------------------------------------------------------------------
# Magic variable references
# ---------------------------------------------------------------------------


def variable_ref(uuid_str: str, output_name: str = "Output") -> dict[str, Any]:
    """Build a reference dict pointing at another action's output.

    Embed the result as the value of a parameter that accepts a magic
    variable. The exact format used by Shortcuts is a "token-attributed
    string" — a string whose value is a single object-replacement char
    plus an attachments map keyed by character offset.

    See docs/plist-structure.md for the gory details.
    """
    return {
        "Value": {
            "string": "\ufffc",  # object replacement character
            "attachmentsByRange": {
                "{0, 1}": {
                    "Type": "ActionOutput",
                    "OutputUUID": uuid_str,
                    "OutputName": output_name,
                }
            },
        },
        "WFSerializationType": "WFTextTokenString",
    }


def text_token(value: str) -> dict[str, Any]:
    """Wrap a literal string as a WFTextTokenString.

    Many string parameters accept either a plain `str` or a token-attributed
    string. Use plain `str` when you can — use this helper only when the
    schema demands the wrapped form (or when mixing literal text with
    variable references).
    """
    return {
        "Value": {"string": value, "attachmentsByRange": {}},
        "WFSerializationType": "WFTextTokenString",
    }


# ---------------------------------------------------------------------------
# Top-level workflow dict
# ---------------------------------------------------------------------------


# These are the standard input content classes a generic shortcut accepts.
# Trim the list if you want a shortcut that only accepts specific input types.
_DEFAULT_INPUT_CONTENT_CLASSES = [
    "WFAppStoreAppContentItem",
    "WFArticleContentItem",
    "WFContactContentItem",
    "WFDateContentItem",
    "WFEmailAddressContentItem",
    "WFGenericFileContentItem",
    "WFImageContentItem",
    "WFiTunesProductContentItem",
    "WFLocationContentItem",
    "WFDCMapsLinkContentItem",
    "WFAVAssetContentItem",
    "WFPDFContentItem",
    "WFPhoneNumberContentItem",
    "WFRichTextContentItem",
    "WFSafariWebPageContentItem",
    "WFStringContentItem",
    "WFURLContentItem",
]


def base_workflow(
    actions: list[dict[str, Any]],
    *,
    icon_color: int = 4274264319,   # blue-ish
    icon_glyph: int = 59511,         # arbitrary SF Symbol
    client_version: str = "2607.1.3",
    min_client_version: int = 900,
) -> dict[str, Any]:
    """Build the full top-level WFWorkflow dict.

    The builder just supplies `actions`; everything else has sane defaults.
    Override icon/version kwargs only if you have a reason.
    """
    return {
        "WFWorkflowActions": actions,
        "WFWorkflowClientVersion": client_version,
        "WFWorkflowMinimumClientVersion": min_client_version,
        "WFWorkflowMinimumClientVersionNoDevice": min_client_version,
        "WFWorkflowIcon": {
            "WFWorkflowIconStartColor": icon_color,
            "WFWorkflowIconGlyphNumber": icon_glyph,
        },
        "WFWorkflowImportQuestions": [],
        "WFWorkflowTypes": [],  # empty = generic / "any"
        "WFWorkflowInputContentItemClasses": list(_DEFAULT_INPUT_CONTENT_CLASSES),
        "WFWorkflowHasOutputFallback": False,
        "WFWorkflowHasShortcutInputVariables": False,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_shortcut(workflow: dict[str, Any], out_path: str | Path) -> Path:
    """Serialize the workflow as a binary plist and verify it round-trips.

    Returns the resolved output path. Raises if the written file fails to
    re-parse — that's our minimum sanity check given we don't have plutil.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("wb") as f:
        plistlib.dump(workflow, f, fmt=plistlib.FMT_BINARY)

    # Round-trip check: re-open and ensure the action count matches.
    with out.open("rb") as f:
        roundtripped = plistlib.load(f)
    assert (
        len(roundtripped["WFWorkflowActions"]) == len(workflow["WFWorkflowActions"])
    ), "Round-trip action count mismatch — plist is malformed"

    n = len(workflow["WFWorkflowActions"])
    print(f"Wrote {out} ({n} action{'s' if n != 1 else ''})")
    return out
