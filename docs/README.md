# Apple Shortcuts — programmatic builder repo

Build Apple Shortcuts (`.shortcut` files) in Python. Sign and import them
on your Mac. They sync to iOS via iCloud.

## Why this repo exists

The Shortcuts app's drag-and-drop UI is unpleasant for non-trivial
automations. This repo treats `.shortcut` files as **build artifacts**
produced by Python code that lives in `builders/`. The Python code is the
source of truth; the `.shortcut` files are regenerable.

## Layout

```
.
├── raw/           ← unsigned .shortcut files (regenerated from builders/)
├── signed/        ← signed .shortcut files (output of sign-all.sh; macOS-only)
├── builders/      ← one .py per shortcut + _shortcut_lib.py shared helpers
└── docs/
    ├── SKILL.md             ← the skill that teaches Claude this workflow
    ├── README.md            ← you are here (well, a copy of you)
    ├── action-reference.md  ← WFWorkflow action identifiers + parameter schemas
    ├── plist-structure.md   ← top-level plist key reference
    ├── sign-all.sh          ← macOS script: sign everything in raw/ → signed/
    └── shortcuts/           ← one .md per shortcut explaining what it does
```

## Workflow

1. Ask Claude to build a shortcut (it has the `apple-shortcut-builder` skill
   in `docs/SKILL.md`).
2. Claude writes `builders/<slug>.py`, runs it, drops `raw/<slug>.shortcut`,
   and writes `docs/shortcuts/<slug>.md`.
3. On your Mac:
   ```bash
   bash docs/sign-all.sh           # signs all → signed/
   open signed/<slug>.shortcut     # imports into Shortcuts app
   ```
4. The Shortcuts app syncs the imported shortcut to your iPhone via iCloud.

## Re-running a builder

Builders are idempotent (modulo random UUIDs). To regenerate a shortcut
after editing its builder:

```bash
python3 builders/<slug>.py
```

## Index of shortcuts

| Slug | Description | Status |
|---|---|---|
| [hello-world](shortcuts/hello-world.md) | Toolchain test: notification + speak text | ✅ Built, awaiting first sign-and-import |

## Requirements

**On your Mac:**
- macOS 12 or later (for the `shortcuts` CLI)
- Python 3.10+

**On Claude's side:**
- Just `plistlib` and `uuid`, both stdlib. No external dependencies.

## What this repo does NOT do

- Sign shortcuts. (`sign-all.sh` does that on your Mac.)
- Configure iOS personal automations like NFC triggers — those are
  device-local on iOS. The shortcut produced here is what the
  automation *runs*; the trigger itself is set up in the Shortcuts app
  on your phone.
- Run shortcuts. Use `shortcuts run "<name>"` on your Mac for that.
