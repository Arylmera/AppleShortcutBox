# `.shortcut` Plist Structure

A `.shortcut` file is an Apple binary property list. `plutil -convert xml1` or
Python's `plistlib` will give you the equivalent dictionary.

The top-level value is a **dictionary** with the keys below. Many keys are
prefixed `WFWorkflow` because Shortcuts is the descendant of the old
"Workflow" app and the format wasn't renamed.

## Top-level keys

| Key | Type | Required | Notes |
|---|---|---|---|
| `WFWorkflowActions` | array of dicts | yes | The ordered list of action dicts. This is the meat of the file. |
| `WFWorkflowClientVersion` | string | yes | E.g. `"2607.1.3"`. Newer Shortcuts apps may rewrite this on first save. If import fails with a version mismatch, export a reference shortcut and copy its value. |
| `WFWorkflowMinimumClientVersion` | int | yes | Minimum Shortcuts app version. `900` is a safe floor for iOS 15+. |
| `WFWorkflowMinimumClientVersionNoDevice` | int | yes | Same value as above, just a separate field for cross-device runs. |
| `WFWorkflowIcon` | dict | yes | See "Icon dict" below. |
| `WFWorkflowImportQuestions` | array | yes | Empty array if the shortcut asks no setup questions on import. Non-empty for shortcuts that prompt the user (e.g. "what's your home address") on first import. |
| `WFWorkflowTypes` | array of strings | yes | Where the shortcut shows up. Empty array = generic. Values include `"Watch"`, `"MenuBar"`, `"NCWidget"`, `"QuickActions"`, etc. |
| `WFWorkflowInputContentItemClasses` | array of strings | yes | What input types the shortcut accepts as the "Shortcut Input" magic variable. The default list in `_shortcut_lib.py` is the everything-allowed superset. |
| `WFWorkflowHasOutputFallback` | bool | yes | Whether the shortcut has a fallback output. False unless you know you need this. |
| `WFWorkflowHasShortcutInputVariables` | bool | yes | Whether the shortcut uses the special "Shortcut Input" variable. |

### Icon dict

```python
{
    "WFWorkflowIconStartColor": 4274264319,   # 32-bit ARGB-ish int
    "WFWorkflowIconGlyphNumber": 59511,       # SF Symbol glyph code
}
```

The color int is an undocumented encoding. The defaults in `_shortcut_lib.py`
produce a blueish icon with a generic glyph. To get a specific look, export a
reference shortcut with the icon you want and copy the values.

## Action dict structure

Each element of `WFWorkflowActions` is:

```python
{
    "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
    "WFWorkflowActionParameters": {
        "UUID": "752B3721-D5AF-48E1-923C-AC5DDF8E46D2",
        "WFNotificationActionTitle": "Hello",
        # ... action-specific params
    },
}
```

### The `UUID` parameter

Every action has a `UUID` inside its parameter dict. It's used for:

1. **Magic variable references** — when a later action references this
   action's output, the reference is by this UUID.
2. **Control flow grouping** — the start, middle, and end actions of an
   If/Repeat/Menu construct share a `GroupingIdentifier` UUID, but each
   action also has its own `UUID`.

Generate UUIDs with `uuid.uuid4()` and store them in a local dict in your
builder so other actions can reference them by logical name.

## Magic variable references

To reference another action's output as a parameter value, use a
**token-attributed string** dict:

```python
{
    "Value": {
        "string": "\ufffc",  # U+FFFC OBJECT REPLACEMENT CHARACTER
        "attachmentsByRange": {
            "{0, 1}": {
                "Type": "ActionOutput",
                "OutputUUID": "<uuid of source action>",
                "OutputName": "Output",  # usually "Output", varies per action
            }
        },
    },
    "WFSerializationType": "WFTextTokenString",
}
```

The `{0, 1}` key is an NSRange string — character range 0, length 1. To embed
a variable in the middle of literal text, use a longer `string` and put the
`\ufffc` placeholder at the right offset, then adjust the range key.

For convenience, `_shortcut_lib.py` provides:
- `variable_ref(uuid_str)` — pure variable, no surrounding text
- `text_token(value)` — literal string in the wrapped form

## Control flow blocks (If, Repeat, Menu)

A construct like If/Otherwise/End If is THREE actions in the array, all sharing:

- The same `WFWorkflowActionIdentifier` (e.g. `is.workflow.actions.conditional`)
- The same `GroupingIdentifier` UUID inside their parameters
- Different `WFControlFlowMode` integers: `0` = start, `1` = middle, `2` = end

So an If/Otherwise/End If becomes:

```python
group_id = new_uuid()

[
    make_action("is.workflow.actions.conditional", {
        "GroupingIdentifier": group_id,
        "WFControlFlowMode": 0,
        "WFCondition": 4,  # "is" — see the action's docs
        "WFConditionalActionString": "yes",
        # the variable being tested goes here, often as WFInput
    }),
    # ... actions to run if true ...
    make_action("is.workflow.actions.conditional", {
        "GroupingIdentifier": group_id,
        "WFControlFlowMode": 1,  # Otherwise
    }),
    # ... actions to run if false ...
    make_action("is.workflow.actions.conditional", {
        "GroupingIdentifier": group_id,
        "WFControlFlowMode": 2,  # End If
    }),
]
```

## Signed shortcuts (AEA)

Shortcuts exported since iOS 15 are wrapped in **Apple Encrypted Archives**
(AEA). The unsigned plist is the inner payload. To work with a signed shortcut:

```bash
# Extract unsigned from signed (using shortcut-sign, not Apple's CLI)
shortcut-sign extract signed.shortcut unsigned.shortcut

# Or, with Apple's CLI, you can re-sign:
shortcuts sign --mode anyone --input unsigned.shortcut --output signed.shortcut
```

This repo always works with **unsigned** plists in `raw/`. The user signs them
with `docs/sign-all.sh` before importing.

## Validation

You can't `plutil -lint` from Linux, but Python's `plistlib.load()` will
refuse to parse a malformed plist, and that's enough as a structural check.
Every builder script does this round-trip via `write_shortcut()` in
`_shortcut_lib.py`.

The TRUE validation is whether the Shortcuts app accepts the import without
"Shortcut Cannot Be Opened" or "Action is Missing" errors. We can only
confirm that on the user's Mac.
