---
name: apple-shortcut-builder
description: Use this skill when the user wants to create, edit, or generate an Apple Shortcut (.shortcut file) programmatically. Triggers on requests like "make me a shortcut that...", "build a shortcut for...", "create a new Apple Shortcut", or any mention of generating .shortcut files, WFWorkflow plists, or NFC-triggered shortcuts. Use this skill in any repo containing the folders raw/, signed/, builders/, and docs/ at its root — these indicate the shortcut-building project structure this skill manages. Do NOT use this skill for running existing shortcuts (that's the `shortcuts run` CLI on macOS) or for iOS personal automation triggers (those are device-local, not part of .shortcut files).
---

# Apple Shortcut Builder

## What this skill does

Generates valid unsigned Apple `.shortcut` files (binary plists) using Python.
The user signs them on their Mac afterwards and imports them into the Shortcuts
app, which syncs to iOS via iCloud.

This skill is intentionally **scoped to the unsigned half of the workflow**.
Signing requires Apple's macOS-only `shortcuts` CLI; you cannot do it. The user
runs a single bash script (`docs/sign-all.sh`) on their Mac to sign everything
in `raw/` and produce signed copies in `signed/`.

## The engine: python-shortcuts (adopted 2026-04-28)

Builders use [`python-shortcuts`](https://github.com/alexander-akhmetov/python-shortcuts)
(`pip3 install --user shortcuts`) as the underlying plist emitter. The wrapper
in `builders/_shortcut_lib.py` re-exports the action classes we use, adds a
`plistlib.Data` shim for Python 3.9+, and provides extensions where the
upstream library is incomplete (notably `IfActionExt` with the full operator
set, since upstream only exposes Equals/Contains).

When you need a new action, **don't roll your own dict** — use or extend
the python-shortcuts class. See `_shortcut_lib.py` for the pattern.

Cross-references for verifying schemas: see [external-libraries.md](external-libraries.md).

## Repo layout this skill assumes

```
.
├── raw/         ← unsigned .shortcut files YOU generate
├── signed/      ← signed .shortcut files the USER generates by running sign-all.sh on macOS
├── builders/    ← one Python script per shortcut, kept forever (these are the source of truth)
└── docs/
    ├── SKILL.md                     ← this file
    ├── action-reference.md          ← known WFWorkflow action identifiers + parameter schemas
    ├── plist-structure.md           ← top-level plist keys and what they mean
    ├── sign-all.sh                  ← the bash script user runs on macOS to sign everything
    ├── README.md                    ← human-facing entry point
    └── shortcuts/
        └── <shortcut-name>.md       ← one doc per shortcut explaining what it does
```

## The workflow, end-to-end

When the user asks for a new shortcut:

1. **Pick a slug.** A short, kebab-case name like `hello-world` or `car-mode`.
   This is the filename stem used everywhere: `builders/<slug>.py`,
   `raw/<slug>.shortcut`, `signed/<slug>.shortcut`, `docs/shortcuts/<slug>.md`.

2. **Write the builder.** Create `builders/<slug>.py`. It MUST:
   - Import the action classes and `write_shortcut` from `builders/_shortcut_lib.py`.
   - Define a `build()` function returning a `list[BaseAction]`.
   - Have a `__main__` block that calls `write_shortcut(build(), raw/<slug>.shortcut)`.
   - Be runnable as `python3 builders/<slug>.py` from the repo root.

3. **Run the builder** to produce `raw/<slug>.shortcut`. Verify with
   `python3 -c "import plistlib; plistlib.load(open('raw/<slug>.shortcut','rb'))"`
   — it must round-trip without error.

4. **Write per-shortcut docs.** Create `docs/shortcuts/<slug>.md` with:
   - One-line summary (used as the description)
   - What it does (numbered steps in plain English)
   - Action identifiers used (linking to `action-reference.md`)
   - Date created
   - Any known caveats (iOS version requirements, etc.)

5. **Update `docs/README.md`** to add the new shortcut to the index table.

6. **Sign and open it.** This user is on macOS and wants the full
   build→sign→import flow to happen automatically. After the builder
   succeeds, run:
   ```bash
   bash docs/sign-all.sh <slug>
   open signed/<slug>.shortcut
   ```
   Only fall back to "tell the user to run it" if the sign step fails
   or you're not on Darwin.

## Critical rules

### Always use the helper library
Every builder imports from `_shortcut_lib.py`. Don't duplicate the
boilerplate (icon dict, content-item-classes list, action wrapper). If a
helper is missing, add it to `_shortcut_lib.py` rather than inlining.

### UUIDs are load-bearing
Every action gets a UUID under `WFWorkflowActionParameters.UUID`. When one
action references another (magic variables, If/Otherwise grouping, Repeat
loops), that reference is by UUID. Generate with `uuid.uuid4().hex.upper()`
(or just `str(uuid.uuid4()).upper()`). Never hand-write them. Keep a dict
mapping logical names to UUIDs inside `build()` so references are readable.

### Validate before claiming success
After writing any `.shortcut`, round-trip it through `plistlib.load()` to
confirm it's well-formed. If you have access to `plutil` (you usually
won't — you're on Linux), also `plutil -lint`. Tell the user to run
`plutil -lint raw/<slug>.shortcut` on their Mac as part of their
verification.

### When unsure about an action identifier or parameter, say so
Action identifiers (e.g. `is.workflow.actions.notification`) and their
parameter schemas are not fully documented by Apple and drift across iOS
versions. If you're unsure:
1. Check `docs/action-reference.md` first — the user may have already
   captured it from a real exported shortcut.
2. If not there, tell the user: "I'm not 100% sure of the parameter
   schema for `<action>`. Can you export a reference shortcut from the
   GUI that uses this action? I'll diff against it and update
   `action-reference.md`."
3. Do NOT guess silently. A wrong identifier means the action shows as
   "missing" on import, which is annoying to debug.

### Keep builders self-contained and re-runnable
`python3 builders/<slug>.py` must always regenerate `raw/<slug>.shortcut`
deterministically (modulo UUIDs, which are random by design). No
side-effects, no network calls.

### Never touch signed/ directly
`signed/` is purely the user's output directory. Do not write there.

### Don't edit ~/Library/Shortcuts directly
That's the live Shortcuts database. The whole point of this repo is to
treat `.shortcut` files as the source of truth and let the user import
them through the official path.

## What goes in `_shortcut_lib.py`

`_shortcut_lib.py` is now a thin wrapper around `python-shortcuts`. Its
responsibilities:

1. **Shim `plistlib.Data`** — python-shortcuts 0.11.0 still uses the
   removed-in-Python-3.9 `plistlib.Data`. We patch it to a no-op
   `lambda` that returns its argument unchanged.
2. **Re-export the action classes builders use** (`NotificationAction`,
   `DateAction`, `FormatDateAction`, `URLAction`, `OpenURLAction`,
   `OpenAppAction`, `EndIfAction`, etc.) from a single import surface.
3. **Define extensions** where upstream is incomplete. Currently:
   - `IfActionExt` — same plist as upstream's `IfAction` but accepts the
     full `WFCondition` operator enum (`Is Less Than`, `Is Greater Than`,
     `Begins With`, `Ends With`, `Has Any Value`, `Does Not Have Any Value`,
     plus `Equals` and `Contains`).
4. **Provide `write_shortcut(actions, out_path)`** — wraps the
   `Shortcut(...).dump(file, FMT_SHORTCUT)` boilerplate plus a round-trip
   sanity check.

When you need a python-shortcuts action that's not yet re-exported from
`_shortcut_lib.py`, add it to the re-export list. When you need an action
or operator that python-shortcuts doesn't support, subclass `BaseAction`
following the `IfActionExt` pattern and document the schema in
`docs/action-reference.md`.

## When a builder needs an action you've never used before

1. Look it up in `docs/action-reference.md`.
2. If it's missing, check `docs/external-libraries.md` — odds are
   python-shortcuts and/or shortcuts-toolkit have the schema. Cross-check
   them; if they agree, add a "🔁 cross-referenced" row to
   `action-reference.md` and re-export the class (or subclass it) in
   `_shortcut_lib.py`.
3. If even those don't have it, ask the user to export a reference
   shortcut from the GUI. Decode with `plistlib.load()`, find the
   action, and add a "✅ verified" entry.
4. THEN write the builder.

## Skill invocation checklist (use this every time)

When you start work on a shortcut request, walk through:

- [ ] Confirm you're in a repo with `raw/`, `signed/`, `builders/`, `docs/`
- [ ] Pick a slug
- [ ] Read `docs/action-reference.md` for any action you plan to use
- [ ] Confirm `_shortcut_lib.py` exists; create it if this is the first shortcut
- [ ] Write `builders/<slug>.py`
- [ ] Run it, verify the output round-trips through `plistlib.load()`
- [ ] Write `docs/shortcuts/<slug>.md`
- [ ] Update `docs/README.md` index
- [ ] Run `bash docs/sign-all.sh <slug>` then `open signed/<slug>.shortcut`

## Things this skill explicitly does NOT do

- Sign shortcuts. (macOS-only; user does it.)
- Configure iOS personal automations (e.g. NFC triggers). Those are
  device-local. The skill produces the shortcut that the automation runs.
- Run shortcuts. (`shortcuts run` is macOS-only.)
- Edit the live Shortcuts database in `~/Library/Shortcuts`.
