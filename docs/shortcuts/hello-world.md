# hello-world

> Minimal end-to-end test: shows a notification, then speaks a line of text.

## What it does

1. Shows a system notification with title "Hello from code" and body
   "This shortcut was built in Python."
2. Speaks the line "Shortcut built from Python" via the system TTS.

## Actions used

| # | Identifier | Purpose |
|---|---|---|
| 1 | `is.workflow.actions.notification` | Show notification |
| 2 | `is.workflow.actions.speaktext` | Speak text |

Both are documented in [../action-reference.md](../action-reference.md).

## Files

- Builder: [`builders/hello-world.py`](../../builders/hello-world.py)
- Unsigned: `raw/hello-world.shortcut`
- Signed: `signed/hello-world.shortcut` (after running `sign-all.sh`)

## Created

2026-04-28

## Caveats

None. This is the canonical "is the toolchain working?" shortcut. If this
fails to import, the problem is environmental (signing, macOS version,
Shortcuts app version) rather than the shortcut itself.
