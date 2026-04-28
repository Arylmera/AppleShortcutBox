# Action Reference

Every Apple Shortcut action has an identifier (e.g. `is.workflow.actions.notification`)
and a parameter schema. Apple does not publish these — they're inferred from
exporting reference shortcuts and reading the plist.

**This file is the source of truth for every action used in this repo.** When
adding a new action, export a reference shortcut from the GUI, decode it, and
add an entry here BEFORE writing the builder.

## Reference shortcut export workflow (on macOS)

```bash
# In the Shortcuts app: build a one-action reference, then File > Export > .shortcut
# Then on the Mac:
plutil -convert xml1 -o reference.xml reference.shortcut
# Or in Python:
python3 -c "import plistlib, json; print(json.dumps(plistlib.load(open('reference.shortcut','rb')), indent=2, default=str))"
```

Find the action in the `WFWorkflowActions` array, copy the identifier and
parameter keys into a new entry below.

---

## Verified actions

### `is.workflow.actions.notification` — Show Notification

Displays a system notification.

| Parameter | Type | Notes |
|---|---|---|
| `WFNotificationActionTitle` | `str` (or token string) | Title line |
| `WFNotificationActionBody` | `str` (or token string) | Body text |
| `WFNotificationActionSound` | `bool` | Optional. Whether to play sound. |

**Example:**
```python
make_action("is.workflow.actions.notification", {
    "WFNotificationActionTitle": "Hello",
    "WFNotificationActionBody": "From Python",
})
```

Status: ✅ Confirmed working in `hello-world` shortcut.

---

### `is.workflow.actions.speaktext` — Speak Text

Reads text aloud via the system TTS.

| Parameter | Type | Notes |
|---|---|---|
| `WFText` | `str` (or token string) | Text to speak. Plain string is fine. |
| `WFSpeakTextRate` | `float` | Optional. 0.0–1.0. |
| `WFSpeakTextPitch` | `float` | Optional. 0.5–2.0. |
| `WFSpeakTextLanguage` | `str` | Optional. BCP-47 code, e.g. `"en-US"`. |
| `WFSpeakTextVoice` | `str` | Optional. Voice identifier. |
| `WFSpeakTextWaitUntilFinished` | `bool` | Optional. Default true. |

**Example:**
```python
make_action("is.workflow.actions.speaktext", {
    "WFText": "Hello world",
})
```

Status: ✅ Confirmed working in `hello-world` shortcut.

---

## Actions to document next (placeholders — schemas not yet verified)

The identifiers below are believed correct but their parameter schemas
have NOT been verified in this repo. When you need one of these, export a
reference shortcut, verify, and move it to the "Verified actions" section.

| Action | Identifier (best guess) |
|---|---|
| Set Variable | `is.workflow.actions.setvariable` |
| Get Variable | `is.workflow.actions.getvariable` |
| If | `is.workflow.actions.conditional` |
| Otherwise / End If | same identifier, different `WFControlFlowMode` |
| Repeat | `is.workflow.actions.repeat.count` |
| Repeat with Each | `is.workflow.actions.repeat.each` |
| Choose from Menu | `is.workflow.actions.choosefrommenu` |
| URL | `is.workflow.actions.url` |
| Get Contents of URL | `is.workflow.actions.downloadurl` |
| Open URL | `is.workflow.actions.openurl` |
| Open App | `is.workflow.actions.openapp` |
| Set Playback Destination | `is.workflow.actions.setplaybackdestination` |
| Play Music | `is.workflow.actions.playmusic` |
| Set Focus | `is.workflow.actions.setfocus` |
| Set Low Power Mode | `is.workflow.actions.lowpowermode.set` |
| Wait | `is.workflow.actions.delay` |
| Comment | `is.workflow.actions.comment` |
| Ask for Input | `is.workflow.actions.ask` |
| Show Result | `is.workflow.actions.showresult` |
| Get Current Location | `is.workflow.actions.location` |

---

## Control flow notes

If/Otherwise/End If, Repeat/End Repeat, and Choose from Menu use a SINGLE
identifier per construct, with a `WFControlFlowMode` integer indicating the
role:

- `0` = start (e.g. "If", "Repeat")
- `1` = middle (e.g. "Otherwise", a menu item)
- `2` = end (e.g. "End If", "End Repeat")

The start, middle, and end actions of one construct share a `GroupingIdentifier`
(a UUID) under their parameters. Generate one UUID per construct and reuse it
across the start/middle/end actions.

This is documented further in `plist-structure.md` once we use it for real.
