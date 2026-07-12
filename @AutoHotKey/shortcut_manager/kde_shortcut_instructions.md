# KDE Plasma Shortcut Migration Instructions

> [!NOTE]
> **To the User**: Provide this markdown file to the AI in your next session. It serves as a detailed blueprint for the AI to translate your AutoHotkey (AHK) code into native Linux scripts and configure them in KDE Plasma.

---

## 🎯 Context & Objective for the AI
The user wants to migrate specific AutoHotkey (AHK) script behaviors to run natively under **Linux KDE Plasma**. The user will provide raw AutoHotkey code blocks, and your job is to translate them into native Linux equivalents (Python, Bash, or D-Bus commands) and explain how to configure them as global shortcuts in KDE Plasma.

### AI Tasks to Perform:
1. **Analyze AHK Code**: Read the user's provided AutoHotkey script or command.
2. **Translate to Native Linux Scripting**:
   - Write equivalent Python or Bash scripts using native tools like `ydotool` (keyboard simulation), `wl-clipboard` (clipboard operations), or standard subprocesses.
3. **Generate KDE Shortcut Configurations**:
   - For GNOME/KDE, show the user how to configure a custom global shortcut to run the translated script.
   - If automated, show how to generate a `.desktop` file for `~/.local/share/applications/` or write to `~/.config/kglobalshortcutsrc`.
4. **Explain GUI Setup**: Provide step-by-step instructions for setting it up in **KDE System Settings $\to$ Shortcuts**.

---

## 🛠️ Step-by-Step Migration Blueprint (For the AI to Execute)

### Step 1: Mapping AHK Syntaxes to Python/Bash
Translate AHK API actions to Linux command-line/scripting equivalents:
* **AHK `Send()` / Keyboard input** $\to$ `ydotool type "text"` or `wtype "text"`.
* **AHK `Run()` / Shell execution** $\to$ Bash command or Python `subprocess.Popen()`.
* **AHK Clipboard (`A_Clipboard`)** $\to$ `wl-copy` and `wl-paste` commands (Wayland) or `xclip` / `xsel` (X11).
* **AHK Active window queries (`WinActive`, `#HotIf`)** $\to$ Command-line queries using `hyprctl activewindow`, `swaymsg`, or `xdotool getactivewindow`.

### Step 2: Creating a KDE Launchable Action
Show the user how to wrap the translated script into a KDE Plasma Custom Shortcut. Let the user know if they can use a standard `.desktop` file structure inside `~/.local/share/applications/`:
```ini
[Desktop Entry]
Type=Application
Name=My Translated Shortcut
Exec=python3 /path/to/translated_script.py
Icon=utilities-terminal
Terminal=false
```

---

## 📋 Instructions for the User (What to do Next)

To run a translation in a future session:
1. Ensure your system dependencies are installed:
   ```bash
   # For clipboard actions on Wayland
   sudo apt install wl-clipboard
   
   # For low-level input simulation (if Wayland)
   sudo apt install ydotool
   ```
2. Upload/paste this file (`kde_shortcut_instructions.md`) and your raw AHK code blocks.
3. Tell the AI: **"Please translate the provided AHK code block into Linux python/bash equivalents and guide me on binding it in KDE Plasma as described in the blueprint."**
