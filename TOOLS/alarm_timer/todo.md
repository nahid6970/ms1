# Alarm Timer - Edit Dialog Fixes

## What was asked:
1. Editing label only (leaving time blank) pauses the timer and never resumes it
2. Edit dialog is missing the datetime picker mode (only has text input)

## Task List

- [X] Fix: resume timer after edit if it was running before (was_running flag)
- [X] Add Text / Pick datetime mode toggle to the edit dialog, same as AddTimerDialog
