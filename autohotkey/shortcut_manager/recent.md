# recent.md — AI Handoff Document

## 1. Project DNA (Permanent)

PyQt6 GUI app (`ahk_gui_pyqt.py`) that manages AutoHotkey v2 shortcuts stored in `ahk_shortcuts.json` and generates a single `generated_shortcuts.ahk` output file. Shortcut types: `script_shortcuts`, `text_shortcuts`, `context_shortcuts`, `startup_scripts`, `launcher_shortcuts`, `remap_shortcuts`, `exclusion_rules`. All features are JSON-only — the GUI reads/writes the JSON, user clicks "Generate AHK" to produce the runnable script.

---

## 2. Latest Implementation (2026-09-28)

### Clipboard Manager (Ditto-style) — `startup_scripts`
- **File:** `ahk_shortcuts.json` → entry name `"Clipboard Manager (Ditto-style)"`
- Hooks `OnClipboardChange`, keeps 9-slot text history (slot 1 = most recent)
- `Ctrl+Alt+Numpad1-9` → paste slot N (restores original clipboard after)
- `Ctrl+Alt+Numpad0` → tooltip showing all 9 slots
- Uses `ClipIgnoreNext` flag to avoid re-capturing its own paste operations

### Macro Recorder rewrite — `startup_scripts`
- **File:** `ahk_shortcuts.json` → entry name `"Macro Recorder"`
- `Ctrl+R` = start/stop recording, `Ctrl+E` = playback
- **Key change:** replaced raw `SendEvent {vkXX down/up}` replay with combo reconstruction via `MacroBuildCombos()` — reads the raw key buffer and converts sequences into proper `Send("^!4")` style strings
- `MacroTrimStopKey()` strips only Ctrl+R tail events (not Alt or other modifiers)
- `held.Delete(vk)` guarded with `held.Has(vk)` to prevent "Item has no value" crash
- Hard modifier release (`LCtrl/RCtrl/LAlt/RAlt` etc.) before and after playback
- `MacroKillGui()` named function replaces inline `SetTimer(() => { })` block (AHK v2 doesn't allow multi-line arrow function bodies)

---

## 3. Critical Context

- **Never use `SetTimer(() => { multi-line })` in AHK v2** — must extract to a named function
- **Never use `Map.Delete(key)` without `Map.Has(key)` guard** — throws "Item has no value"
- **`SendEvent {vkXX down/up}` is unreliable for modifier keys** — always use `Send("^!x")` style combos for reliable modifier handling
- The `context_mode: "inactive"` field on Macro Recorder means it is *excluded* from the RUNNER terminal window, not restricted to it
- Output AHK file path: `C:\@delta\output\ahk\generated_shortcuts.ahk`

---

## 4. Pending Task

Nothing critical pending. Next natural improvement: add a way to name/save multiple macros (currently only one macro slot exists).
