# carplay-morning

One-line: when run, opens Waze and starts Spotify Liked Songs — but only if the local time is before 07:00.

## What it does

1. Gets the current date.
2. Formats it as the 24-hour hour-of-day (`H` → "0".."23").
3. Coerces that to a Number.
4. If the hour is less than 7:
   - Opens `waze://` (launches Waze).
   - Opens `spotify:collection:tracks` (Spotify Liked Songs view).
5. End If.

If the hour is ≥ 7, the shortcut does nothing.

## How to wire it up to CarPlay

The CarPlay-connect trigger is an iOS *personal automation*, not part of the `.shortcut` file. After importing:

1. iPhone → Shortcuts app → Automation tab → "+" → Create Personal Automation.
2. Choose **CarPlay** → **Connects** → Next.
3. Action: **Run Shortcut** → pick `carplay-morning` → Next.
4. Turn off "Ask Before Running" if you want it silent.

## Action identifiers used

All cross-referenced — see [action-reference.md](../action-reference.md):

- `is.workflow.actions.date`
- `is.workflow.actions.format.date`
- `is.workflow.actions.conditional` (start + end, via `IfActionExt`)
- `is.workflow.actions.url`
- `is.workflow.actions.openurl`

## How the If wires up

The If action has no explicit input field — it reads the *previous*
action's output. Format Date sits directly above the If, so the If
compares the formatted hour string ("0".."23") against `"7"`.
`Is Less Than` does numeric comparison when both sides look like
numbers.

## Caveats

- **Spotify URL scheme**: `spotify:collection:tracks` opens the Liked Songs view; on iOS it doesn't always autoplay. If you want autoplay, the Spotify-provided "Play" Shortcuts action would be more reliable — that needs a reference export so we can capture its identifier and parameter schema.
- **Waze must be installed**, signed in, and have notification/location permissions set up the way you normally use it.
- The hour test uses the device's local timezone.

## Iteration history

**v1** (rolled by hand): the If had `WFCondition: 2` (integer guess) and
`WFNumberValue: 7` plus a useless Number coercion action. Imported but
the GUI showed the If with no bound condition.

**v2** (python-shortcuts): switched the If to `WFCondition: "Is Less
Than"` (string) and put the comparison value in `WFConditionalActionString`
because that's what python-shortcuts and shortcuts-toolkit both
documented. Imported and showed `If Formatted Date is less than Number`
— but the "Number" was empty because string-comparison field doesn't
populate the numeric input slot.

**v3** (this version): for numeric operators the comparison value goes
in `WFNumberValue`, NOT `WFConditionalActionString`. Verified via the
[cherri](https://github.com/electrikmilk/cherri) compiler's source.
Both libraries miss this distinction; cherri has it. We taught
`IfActionExt` about both fields so future builders pick the right one
based on the operator.

## Date created

2026-04-28
