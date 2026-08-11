# Problems & Fixes Log

## 2026-06-10 12:00 - Context matching treated comma-separated values as one string

**Problem:** Context shortcut fields like window title, process name, and window class accepted comma-separated text in the GUI, but generation treated the whole field as a single literal string.

**Root Cause:** The generator emitted one `InStr(...)` or equality check per field without splitting comma-separated entries.

**Solution:** Split each field on commas, trim values, and emit `OR` conditions for multiple values.

**Files Modified:**

- `ahk_gui_pyqt.py`

## 2026-06-10 12:00 - Need for app-level shortcut exclusion

**Problem:** Some applications have built-in shortcuts that conflict with AHK hotkeys and hotstrings.

**Root Cause:** The generated script had no global exclusion layer.

**Solution:** Added `exclusion_rules` plus `IsShortcutExcluded()` and wrapped generated shortcut sections with `#HotIf !IsShortcutExcluded()`.

**Files Modified:**

- `ahk_gui_pyqt.py`
- `ahk_shortcuts.json`


## 2026-06-10 17:05 - Exclusion rules saved as text shortcuts and causing AHK reload error

**Problem:** Adding an exclusion rule saved it under the Text Shortcut section, and generating the AHK script resulted in an invalid hotstring `:X:::Paste('')` (missing abbreviation error).

**Root Cause:** In `AddEditShortcutDialog.accept_dialog`, the logic for adding a new shortcut did not check for `self.shortcut_type == "exclude"`, causing new exclusion rules to default to the `text_shortcuts` list.

**Solution:** Included the `"exclude"` check to append rules to `self.parent_window.exclusion_rules`. Additionally, added a database self-healing check in `load_shortcuts_json` to automatically detect and migrate misplaced exclusion rules or context shortcuts from `text_shortcuts` to their correct arrays.

**Files Modified:**
- `ahk_gui_pyqt.py`

## 2026-06-10 17:15 - AHK local variable warning in exclusion rules and output path relocation

**Problem:** 
1. AutoHotkey v2 loaded with a warning: `Warning: This local variable appears to never be assigned a value. Specifically: processName`.
2. AHK script was generated in `C:\@delta\output\ahk` instead of the local project directory.

**Root Cause:**
1. `IsShortcutExcluded()` in the generated script evaluated expressions like `processName = "WindowsTerminal.exe"` but never initialized the local variables `processName`, `windowTitle`, or `windowClass`.
2. The generator output path was hardcoded to `C:\@delta\output\ahk`.

**Solution:**
1. Updated `append_exclusion_checker` to dynamically check if the enabled rules require window title, process name, or class and inject `WinGetTitle`, `WinGetProcessName`, or `WinGetClass` statements respectively inside `IsShortcutExcluded()`.
2. Changed generator `output_dir` from the hardcoded folder to `SCRIPT_DIR` so `generated_shortcuts.ahk` is created inside the project directory.

**Files Modified:**
- `ahk_gui_pyqt.py`
- `dev.md`

## 2026-07-19 07:14 - AHK v2 Array is Empty error when going back

**Problem:** Navigating back in submenus caused a crash: `Error: Array is empty` pointing to `parentObj := CustomMenuGUI.guiStack.Pop()`.

**Root Cause:** A race condition allowed navigation triggers to execute twice before the stack operation completed, attempting to pop an already empty array.

**Solution:** Popped the stack parent atomically before yielding execution to UI transitions, adding safety length checks to `guiStack.Length` in both `GoBack` and keyboard navigation.

**Files Modified:**
- `ahk_gui_pyqt.py`

## 2026-07-19 07:13 - AHK v2 Gui has no window error during menu transitions

**Problem:** Showing menus occasionally crashed the script: `Error: Gui has no window` when trying to register GUI events or show a menu.

**Root Cause:** Event handlers were registered after the GUI window creation asynchronously, or `.Show()` was called before the OS window handle was fully prepared.

**Solution:** Immediate event handler registration right after `Gui(...)` instantiation and wrapped all `.Show()` calls inside `try-catch` blocks.

**Files Modified:**
- `ahk_gui_pyqt.py`

## 2026-07-19 07:19 - AHK v2 Invalid callback function for SetTimer

**Problem:** Hovering over items caused a crash: `Error: Invalid callback function` when attempting to stop the hover timer via `SetTimer(CustomMenuGUI.OnHoverTimer, 0)`.

**Root Cause:** AHK v2 has strict constraints on passing static methods directly as callbacks to timers or hooks, leading to invalid handle references.

**Solution:** Routed timer callbacks through global proxy functions (e.g., `CustomMenuGUI_HoverTimer`) rather than static class methods.

**Files Modified:**
- `ahk_gui_pyqt.py`

## 2026-07-19 08:05 - Selection menus remain stuck open on the screen

**Problem:** When hovering between main menus and submenus, or clicking elsewhere on the screen, menus sometimes remained stuck open or required repeated click/hover interactions to close.

**Root Cause:** 
1. When backtracking on hover, the parent menu was never activated or refocused, leaving the OS active window state out of sync.
2. The deactivation handler `OnActivate` only checked deactivation for the leaf menu (`CustomMenuGUI.guiObj.Hwnd`), ignoring focus shifts from parent menu windows.

**Solution:** 
1. Added `try CustomMenuGUI.guiObj.Show()` during mouse backtracking (`OnMouseMove`) to explicitly reactivate the parent GUI.
2. Updated `OnActivate` to verify deactivation for any menu window in the stack, and check if the newly activated window (`lParam`) belongs to our menu stack. If focus shifts to any external window, `CloseAll()` is triggered.

**Files Modified:**
- `ahk_gui_pyqt.py`
- `md/RECENT.md`
- `md/PROBLEMS_AND_FIXES.md`

## 2026-07-19 14:00 - Selection Menu Bug: Redundant submenu transition loops when clicking parent items

**Problem:** If an item in the selection menu dropdown has subitems, clicking the item itself rather than hovering would cause the UI to become buggy, hovering would stop working, and AHK would require a reload/restart.

**Root Cause:** Clicking a parent item triggered `OnItemClick` which executed the submenu transition logic concurrently with the hover auto-expansion trigger, resulting in double-activation and mismatched GUI stacks.

**Solution:** Added safety guard conditions in both `OnItemClick` and `EnterSubmenu` in `CustomMenuGUI` to check `isTransitioning` and return early if a transition is already in progress.

**Files Modified:**
- `ahk_gui_pyqt.py`

## 2026-07-19 14:15 - Selection Menu Crash: Invalid index error on item click

**Problem:** Clicking some menu items threw a runtime crash: `Error: Invalid index. Specifically: 3` pointing to `item := CustomMenuGUI.activeMenu.items[itemIdx]`.

**Root Cause:** The click callback references the global variable `CustomMenuGUI.activeMenu`. If a transition occurred or the state changed during the click/release cycle, `activeMenu` could point to a different menu object than the one containing the clicked button, leading to out-of-bounds index errors.

**Solution:** Bound the specific menu object `menuObj` directly to each item's button callback wrapper in the GUI creation loop, ensuring it retrieves the item from the correct menu instance rather than relying on the mutable global `activeMenu`.

**Files Modified:**
- `ahk_gui_pyqt.py`





