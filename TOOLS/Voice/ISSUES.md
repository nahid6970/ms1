# Voice Tool - Known Issues

## Chrome Engine: Space Stop Not Working

**Status:** Unresolved

### Problem
Space stop does not work when using the Chrome Extension engine. Pressing Space instantly turns the status green but does nothing — the extension keeps recording.

### Root Cause
- The chrome extension popup is a **separate browser popup** with its own WebSocket connection to Python
- When the user presses Space, the extension popup may already be closed (recognition ended), so `ws_clients` is empty and `send_ws_stop()` sends to nobody
- Even if the popup is open, `recognition.continuous = false` means the extension auto-stops after one phrase anyway — there's no long-running recording to stop
- Python has no way to know if the extension is currently open/recording

### What Works
- Space stop works correctly with **Local engine** (`SpaceStopThread`)
- Chrome engine correctly receives transcripts and pastes them via WebSocket

### What Needs To Be Done
Two options:

**Option A:** Make `Alt+H` open the chrome extension popup programmatically (requires knowing the extension ID and using `chrome.management` or a native messaging approach)

**Option B:** Disable space stop for chrome engine entirely and show a note in settings that SPC mode only applies to local engine

### Affected Files
- `voice_input.py` — `on_press` handler, `send_ws_stop()`
- `google_talk/popup.js` — `onmessage` handler (already added, but popup lifecycle is the blocker)
