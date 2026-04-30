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

## Confidence levels

- **✅ Verified** — exported a reference `.shortcut` from the Shortcuts
  GUI, decoded it, and confirmed the schema in this repo.
- **🔁 Cross-referenced** — the schema agrees across at least two
  external sources (see [external-libraries.md](external-libraries.md)),
  but we have not personally exported a reference yet.
- **🟡 Best-guess** — community reports only; verify before relying on
  it in production.

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

## Cross-referenced actions

These have agreement across `python-shortcuts` and `shortcuts-toolkit`
(see [external-libraries.md](external-libraries.md)) but have not yet
been confirmed by exporting a GUI reference shortcut.

### `is.workflow.actions.date` 🔁 — Current Date

No parameters. Outputs the current date/time.

(Discrepancy: `shortcuts-toolkit` lists this as
`is.workflow.actions.currentdate`. We default to the python-shortcuts
spelling. Verify on next reference export.)

### `is.workflow.actions.format.date` 🔁 — Format Date

| Parameter | Type | Notes |
|---|---|---|
| `WFDateFormat` | string | When using a *custom* format, this holds the format string itself, e.g. `"H"` for 24h hour-of-day. (Counter-intuitive — see warning below.) |
| `WFDateFormatStyle` | string | The format mode. For named modes: `"Short"`, `"Medium"`, `"Long"`, `"Relative"`, `"RFC 2822"`, `"ISO 8601"`. For a custom format string in `WFDateFormat`, use `"Custom"`. |
| `WFDate` | variable ref | Optional. If omitted, operates on the previous action's output. |

⚠️ **The two keys are semantically swapped from what you'd expect.**
`WFDateFormatStyle` holds the *enum* (`"Custom"`) and `WFDateFormat`
holds the actual *format string* (`"H"`). This is what python-shortcuts
emits and what we observed working in the GUI — `shortcuts-toolkit`
documents these reversed, but its claim doesn't match the binary
layout we generated and saw rendered correctly. Trust this row.

### `is.workflow.actions.conditional` 🔁 — If / Else / End If

A single identifier serves all three roles, distinguished by
`WFControlFlowMode`.

| Parameter | Type | Notes |
|---|---|---|
| `WFCondition` | enum string | One of: `Equals`, `Contains`, `Is Greater Than`, `Is Less Than`, `Begins With`, `Ends With`, `Has Any Value`, `Does Not Have Any Value`. STRING, not int. |
| `WFConditionalActionString` | string or variable ref | Comparison value when the operator is a STRING operator (`Equals`, `Contains`, `Begins With`, `Ends With`). |
| `WFNumberValue` | number | Comparison value when the operator is a NUMERIC operator (`Is Less Than`, `Is Greater Than`, and `Equals`-on-numbers). Bare integer in the plist, no `WFTextTokenString` wrapping. |
| `WFAnotherNumber` | number | Second comparison value, only for "is between" style operators (range checks). |
| `WFInput` | variable ref | Optional. The input to test. If omitted, the If operates on the previous action's output. |
| `GroupingIdentifier` | UUID string | Same UUID across the matching `If` start, `Else`, and `End If` actions. |
| `WFControlFlowMode` | int | `0` = If (start), `1` = Else (middle), `2` = End If. |

⚠️ **Pick the right comparison field for the operator.** Numeric
operators silently render as an empty "Number" placeholder in the GUI
when you put the value in `WFConditionalActionString` instead of
`WFNumberValue` — that's exactly what bit `carplay-morning v2`.
Verified via the [cherri](https://github.com/electrikmilk/cherri)
compiler's `shortcutgen.go:960-966`.

### `is.workflow.actions.url` 🔁 — URL

| Parameter | Type | Notes |
|---|---|---|
| `WFURLActionURL` | string | The URL value. Outputs a URL object. |

### `is.workflow.actions.openurl` 🔁 — Open URL

| Parameter | Type | Notes |
|---|---|---|
| `WFURL` | string or variable ref | The URL to open. If absent, opens the previous action's output. |

⚠️ The parameter is `WFURL`, not `WFInput`. The `carplay-morning v1`
builder had this wrong.

### `is.workflow.actions.openapp` 🔁 — Open App

| Parameter | Type | Notes |
|---|---|---|
| `WFAppIdentifier` | string | App bundle id (e.g. `"com.spotify.client"`). |

### `is.workflow.actions.number` 🔁 — Number

| Parameter | Type | Notes |
|---|---|---|
| `WFNumberActionNumber` | number OR variable ref (attachment) | If a literal number, the action emits that constant. If a magic-variable reference (token-attributed string), the action emits the referenced value re-typed as Number — that's how you coerce a string output to Number. |

⚠️ **Numeric If conditions need typed-Number inputs.** `Is Less Than`
on a string runs LEXICOGRAPHIC comparison (so `"10" < "7"` is true
because `'1' < '7'` as characters). To avoid this, route the value
through a Set Variable + Number action with a magic-var reference
before comparing. We use `NumberCoerceAction` in
`builders/_shortcut_lib.py` for this.

---

## Best-guess actions (not yet cross-referenced)

| Action | Identifier (best guess) |
|---|---|
| Set Variable | `is.workflow.actions.setvariable` |
| Get Variable | `is.workflow.actions.getvariable` |
| Repeat | `is.workflow.actions.repeat.count` |
| Repeat with Each | `is.workflow.actions.repeat.each` |
| Choose from Menu | `is.workflow.actions.choosefrommenu` |
| Get Contents of URL | `is.workflow.actions.downloadurl` |
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
