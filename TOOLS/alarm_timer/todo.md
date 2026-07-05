# Alarm Timer - Persist Running State Across Restarts

## What was asked:
When the app restarts, running timers should continue counting from where they left off (not reset/pause). Save a wall-clock timestamp when a timer starts so the elapsed time can be calculated on reload.

## Task List

- [X] Add `started_at` (Unix timestamp) field to TimerCard — set when timer starts/resumes, cleared on pause/reset
- [X] Update `to_dict` to save `started_at`
- [X] Update `from_dict` to: if state was RUNNING, compute remaining = saved_remaining - (now - started_at), then auto-resume the ticker
- [X] Handle edge case: if computed remaining <= 0 on restore, fire the alarm immediately
- [X] Handle PAUSED state restore: keep the saved remaining (no started_at math needed), restore as paused (orange) so user can resume
