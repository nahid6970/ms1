# Alarm Timer - fires_at Absolute Timestamp Refactor

## What was asked:
When picking a date/time, store the exact target Unix timestamp (fires_at) so the countdown
is always computed as (fires_at - now). This makes restarts, pauses and resumes trivial —
no started_at math, no drift.

## Task List

- [X] Add fires_at field to TimerCard (replaces started_at)
- [X] Refactor _tick to use (fires_at - now) instead of decrementing remaining
- [X] Refactor _on_start to set fires_at = now + remaining (or keep existing fires_at)
- [X] Refactor _on_pause to snapshot remaining, clear fires_at
- [X] Refactor _on_reset to clear fires_at
- [X] Update to_dict / from_dict to save/restore fires_at
- [X] Update AddTimerDialog so datetime mode passes fires_at through and auto-starts
- [X] Update _on_edit so datetime mode sets fires_at directly
