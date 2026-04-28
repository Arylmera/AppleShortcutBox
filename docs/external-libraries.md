# External libraries and references

Sources we've cross-referenced to verify Apple Shortcuts action schemas.
This file is the index — the actual schemas live in
[action-reference.md](action-reference.md) (our repo's source of truth).

When `action-reference.md` says a schema is "cross-referenced", it means
the parameter keys and value types agree across at least two of the
sources below. That's our second-best confidence level (still beneath
"exported a reference .shortcut from the GUI and decoded it").

---

## 1. `python-shortcuts` (Python, archived)

- Repo: https://github.com/alexander-akhmetov/python-shortcuts
- PyPI: `pip install shortcuts`
- Status: **archived June 2024** — no upstream fixes for newer iOS versions.
- Style: TOML or Python class API → binary plist `.shortcut` file.
- Last cloned to `/tmp/python-shortcuts` on 2026-04-28.

**What's useful here**

The library's Python source maps each action's logical fields to their
`WF...` plist keys. The most useful files:

| File | Action group | Key takeaways |
|---|---|---|
| `shortcuts/actions/conditions.py` | If / Else / EndIf | Confirms `WFCondition` (string), `WFConditionalActionString` (compare-to value), `GroupingIdentifier`, `WFControlFlowMode` (0/1/2). Only exposes `Equals`/`Contains` operators in its enum, but the underlying plist accepts more (see toolkit below). |
| `shortcuts/actions/date.py` | Date / Format Date | `is.workflow.actions.date` for "Current Date" (toolkit calls it `currentdate` — see discrepancy note below), `is.workflow.actions.format.date` for Format Date. |
| `shortcuts/actions/web.py` | URL / Open URL / Get Contents | `is.workflow.actions.url` (`WFURLActionURL`), `is.workflow.actions.openurl` (no explicit input field — operates on previous action's output). |
| `shortcuts/actions/scripting.py` | Open App / Repeat / Choose from Menu / Wait | `OpenAppAction` uses `WFAppIdentifier` as the field. |
| `shortcuts/actions/numbers.py` | Number | `WFNumberActionNumber` for the literal value. |

**How we use it**: as a reference, not a runtime dependency. Read the
source to confirm a field name, then encode it ourselves via
`_shortcut_lib.py`.

**Why not adopt it directly**: archived; missing the operators we need
for numeric If conditions; TOML-first API doesn't match our
Python-dict-builder approach.

---

## 2. `shortcuts-toolkit` (JavaScript / Node)

- Repo: https://github.com/drewburchfield/shortcuts-toolkit
- Status: documentation project; one commit; not actively maintained.
- Last cloned to `/tmp/shortcuts-toolkit` on 2026-04-28.

**What's useful here**

The single file `action-library.js` is a comprehensive catalog of
action identifiers and parameter schemas, grouped by category, each
tagged with a confidence level (the file only exposes 99%-confidence
ones). It explicitly lists enum *options* — including the full list of
`WFCondition` operators that `python-shortcuts` doesn't expose.

| Category | Notable schemas |
|---|---|
| `web` | `is.workflow.actions.url` → `WFURLActionURL`; `is.workflow.actions.openurl` → `WFURL`; `is.workflow.actions.downloadurl` for HTTP. |
| `text` | `text`, `gettext`, `changebcase` (with case enum), `replacetext`, `splittext`, `combinetext`. |
| `clipboard` | `getclipboard`, `setclipboard` (`WFLocalOnly`, `WFExpirationDate`). |
| `variables` | `setvariable`, `getvariable`, `appendvariable`. |
| `notifications` | `notification`, `alert` (`WFAlertActionTitle`, `WFAlertActionMessage`), `showresult`, `vibrate`. |
| `control` | `conditional` with full `WFCondition` enum (see below); `repeat.count`, `repeat.each`, `choosefrommenu`, `wait`, `stop`. |
| `io` | `ask` (`WFAskActionPrompt`, `WFInputType`: Text/Number/URL/Date/Time/Date and Time), `count` (Items/Characters/Words/Sentences/Lines). |
| `lists` | `getitemfromlist` (First/Last/Random/At Index/In Range), `list`, `filter.files`. |
| `datetime` | `currentdate` (note: differs from python-shortcuts' `date`), `adjustdate` (Add/Subtract/Get Start of …), `format.date` (`WFDateFormat` enum: Short/Medium/Long/Relative/RFC 2822/ISO 8601/Custom; `WFDateFormatStyle` for custom string). |
| `math` | `number` (`WFNumberActionNumber`), `math` (operations including +, −, ×, ÷, Modulus, Square Root, Round, …). |

**The full `WFCondition` enum** (from `action-library.js:343`):

```
'Equals', 'Contains', 'Is Greater Than', 'Is Less Than',
'Begins With', 'Ends With', 'Has Any Value', 'Does Not Have Any Value'
```

These are STRINGS in the plist (not integer codes).

---

## Cross-source discrepancies to be aware of

| Concern | python-shortcuts | shortcuts-toolkit | Resolution |
|---|---|---|---|
| Current-date action identifier | `is.workflow.actions.date` | `is.workflow.actions.currentdate` | Both observed in the wild; iOS likely accepts either. We default to `is.workflow.actions.date` (matches what python-shortcuts emits and what we shipped in `carplay-morning`). Verify on next reference export. |
| Format-Date custom-format key | format string at `WFDateFormat`, enum (`"Custom"`) at `WFDateFormatStyle` | reversed: enum at `WFDateFormat`, custom string at `WFDateFormatStyle` | **python-shortcuts is correct.** We confirmed this empirically: a `.shortcut` we generated with the python-shortcuts mapping rendered correctly in the iOS Shortcuts GUI (Date Format → "Custom", Format String → "H"). Trust python-shortcuts; the toolkit docs are reversed. |
| Open URL input field | implicit (operates on previous action output) | `WFURL` | These are not contradictory — `WFURL` accepts a magic-variable token; if absent, Shortcuts falls back to the previous action's output. Set `WFURL` explicitly when chaining a URL action. |
| If-condition operators | exposes only `Equals` / `Contains` | full 8-operator enum | The plist accepts the full enum; python-shortcuts is just incomplete. Use the toolkit's list. |
| If-condition value type | string at `WFConditionalActionString` | string at `WFConditionalActionString` | Agreed. NOT `WFNumberValue`. |

---

## Other references worth knowing about

- **The Apple Wiki — WorkflowKit framework**:
  https://theapplewiki.com/wiki/Dev:WorkflowKit.framework — high-level
  notes on the private framework that Shortcuts is built on.
- **Decompiling Apple Shortcuts gist** (0xdevalias):
  https://gist.github.com/0xdevalias/27d9aea9529be7b6ce59055332a94477 — community
  notes on extracting and reading shortcut binary plists.
- **Python's `plistlib`**: stdlib reader/writer for both XML and binary
  plists. We rely on this for `write_shortcut()` and round-trip checks.

---

## Process for adding a new action to `action-reference.md`

1. Look it up in `python-shortcuts/shortcuts/actions/<file>.py` for the
   field-to-WFkey mapping.
2. Cross-check `shortcuts-toolkit/action-library.js` for the parameter
   types and any enum option lists (operators, units, modes, …).
3. If both agree → add to `action-reference.md` marked
   "cross-referenced". If they disagree → record the discrepancy here
   and ask the user for a reference shortcut export to break the tie.
4. Once we've verified an action against an actual GUI-exported
   shortcut, upgrade its row in `action-reference.md` to "verified".
