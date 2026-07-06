# `fires_at`-Only Timer Refactor

## Goal

Simplify the timer model so each alarm is represented by one absolute future timestamp only:

```json
{
  "id": "a8fe8ca7",
  "label": "1st of Each Month",
  "fires_at": 1785564000.694
}
```

The timer should fire when `time.time()` reaches `fires_at`. There should be no need to persist or restore:

- `total_seconds`
- `remaining`
- `state`
- pause/resume behavior

## Desired Behavior

1. Creating a timer sets `fires_at` directly.
2. Editing a timer updates `fires_at` directly.
3. On app restart, every timer is reconstructed from `fires_at`.
4. If `fires_at` is in the past on startup, the alarm should fire immediately or be marked due.
5. The UI can still show a countdown, but that countdown should be derived from `fires_at` only.
6. If a timer is conceptually "paused", that concept should be removed rather than persisted.

## What to Remove

- Any dependence on `total_seconds` as persisted source of truth.
- Any dependence on `remaining` as persisted source of truth.
- Any `running` / `paused` / `done` persistence model.
- Any pause button or pause state handling.
- Any restore logic that tries to rebuild a timer from old duration state.

## What to Keep

- Timer label.
- Unique timer id.
- Exact `fires_at` timestamp.
- Countdown display based on `max(0, fires_at - time.time())`.
- Alarm firing logic when current time reaches `fires_at`.

## Extensible Input Modes

The input area should be designed so additional radio options can be added later without changing the timer core.

Examples of future modes:

- `HH:mm at dd MMM`
- `MM yy`
- `yy-MM-dd HH:mm`
- any other custom pattern that resolves to one absolute future timestamp

Each extra radio option should:

1. Show its own input field or picker panel.
2. Parse the user input into one future `fires_at` value.
3. Reuse the same save/load model.

## Pattern Help UI

Add an info icon near the input-mode section. Clicking or hovering it should show a compact pattern reference so the format rules are easy to inspect while editing.

The help text should explain what placeholders mean, for example:

- `HH` = 24-hour hour with leading zero
- `hh` = 12-hour hour with leading zero
- `mm` = minute with leading zero
- `dd` = day of month with leading zero
- `MMM` = short month name
- `MMMM` = full month name
- `yy` = two-digit year
- `yyyy` = four-digit year

The exact pattern language can be whatever the app uses internally, but the UI should make it clear what the tokens mean and how to combine them.

## Implementation Notes

- The save file should serialize only the minimum needed fields, ideally:
  - `id`
  - `label`
  - `fires_at`
- The add/edit dialogs should accept either:
  - a pasted datetime like `17:42 on 22 Jul`
  - a calendar/datetime picker
- Both inputs should resolve to one absolute timestamp.
- The main tick loop should compute countdown display from `fires_at` and trigger once due.
- If a timer has no `fires_at`, it should be considered invalid or unscheduled.

## Open Questions

- Should fired timers remain in the list after firing, or be removed automatically?
- If the app starts and a stored `fires_at` is already past, should it pop immediately or mark as overdue in the UI first?
- Should recurring timers be added later as a separate feature instead of overloading this model?
- Should the pattern help be a tooltip, side panel, or modal popover?
