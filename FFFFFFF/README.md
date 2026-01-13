# AutoHotkey (AHK) GUI Manager

A powerful PyQt6 application for visually managing, searching, and generating AutoHotkey v2 scripts. This tool eliminates the need for manual script editing and provides a "Shortcut Builder" to avoid system-level hotkey conflicts during setup.

## 🚀 Key Features

- **Visual Shortcut Builder (⌨)**: Construct complex hotkeys (like `Ctrl+Alt+T`) by clicking modifier buttons and searching for keys. No more system-level shortcuts triggering while you try to assign them!
- **Searchable Interface**: Instantly find shortcuts by name, key, description, or category.
- **Category Organization**: Group shortcuts into categories (System, Navigation, Media, etc.) with custom color coding.
- **Two Shortcut Types**:
    - **Script Shortcuts**: Runs AutoHotkey v2 code when a hotkey is pressed.
    - **Text Shortcuts (Hotstrings)**: Replaces a typed trigger (e.g., `;v2`) with replacement text. **Automatically handles special characters (#, !, etc.) and multiline text literally.**

---

## 🛠 How to Add New Scripts

To add a new script to the GUI, follow these steps:

1. **Launch the App**: Run `ahk_gui_pyqt.py`.
2. **Add Shortcut**: Click the **+ Add** button and select **Script Shortcut**.
3. **Set Hotkey**: Use the keyboard icon (**⌨**) next to the Hotkey field to open the **Shortcut Builder**. Click Ctrl/Alt/Shift and select your main key.
4. **Input Action**: Paste your AHK v2 code into the **Action** text box.

### Important: Multi-line Logic
- If your script is a **single line** (e.g., `Run "notepad.exe"`), the GUI will generate it as `Hotkey::Action`.
- If your script has **multiple lines**, the GUI **automatically wraps** it in `{ }` braces. You don't need to add them yourself unless you are defining internal functions or blocks.

---

## 📝 AHK v2 Script Examples

Here are some common snippets you can copy and paste into the **Action** box:

### Open a Website
```autohotkey
Run "https://www.google.com"
```

### Launch an App (with specific working directory)
```autohotkey
Run "C:\Path\To\YourApp.exe", "C:\Path\To\"
```

### Type Custom Text (using Send)
```autohotkey
Send "Best regards,{Enter}Nahid Ahmed"
```

### Move/Resize Window
```autohotkey
WinMove(0, 0, 800, 600, "A") ; Moves the Active window to top-left and resizes
```

### Toggle Volume
```autohotkey
Send "{Volume_Mute}"
```

### Multi-line Power Script
```autohotkey
if WinExist("ahk_class Notepad")
    WinActivate
else
    Run "notepad.exe"
```

---

## 📂 Project Structure

- `ahk_gui_pyqt.py`: The main Python application logic and UI.
- `ahk_shortcuts.json`: Your database of saved shortcuts (automatically managed).
- `generated_shortcuts.ahk`: The output file you run with AutoHotkey v2.

## ⚠️ Requirements

- **Python 3.10+**
- **PyQt6**: `pip install PyQt6`
- **AutoHotkey v2**: Required to run the generated `.ahk` file.
