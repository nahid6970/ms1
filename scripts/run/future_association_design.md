# Future Windows File Association Implementation Plan

This document outlines the desired functionality, current implementation details, technical constraints on Windows 10/11, and suggestions for alternative programmatic solutions in the future.

---

## 1. Core Objective

The goal is to allow the **`editor_chooser.py`** application to programmatically set the **global Windows default application** for specific file extensions (e.g., `.json`, `.md`, `.txt`, `.ps1`) on the fly. 

### Desired Workflow:
1. Open the chooser on a file (e.g., via AHK).
2. Toggle the **`DEFAULT`** switch on.
3. Click an editor (e.g., *Notepad++*).
4. **Result:** The chosen editor becomes the default handler in Windows immediately:
   - Double-clicking the file in File Explorer directly opens that editor.
   - The file icon in File Explorer changes to the chosen editor's icon.
   - **Crucially:** Launching via AHK still opens the `editor_chooser.py` screen (so the chooser remains available for quick manual overrides).

---

## 2. Windows 10/11 Technical Constraints

Standard user-level registry modifications to default associations are blocked on modern versions of Windows:
* **`UserChoice` Protection:** Explorer stores the default association under `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\<.ext>\UserChoice`.
* **Hash Integrity Check:** Windows signs the key value with a proprietary, user-specific hash. If an external application modifies this registry key directly, Windows invalidates it and resets the extension to default Windows handlers (like standard Notepad).
* **Kernel Protection (UCPD):** Modern Windows updates employ the *User Choice Protection Driver* (UCPD) which actively denies write/delete access to `UserChoice` keys even to administrative processes.

---

## 3. Current Workaround

To avoid Windows resetting the associations, we currently use a semi-automated, non-intrusive method:
1. **Dynamic ProgID Handlers:** When setting a default, the script registers a custom ProgID: `HKCU\Software\Classes\EditorChooser.<ext>`.
2. **Dynamic Icon Mapping:** The `DefaultIcon` of the custom ProgID is modified dynamically to match the chosen editor (e.g. *Notepad++*, *VSCode*, *Zed*, or *PowerShell*).
3. **Open With Registration:** The custom ProgID is added to the extension's `OpenWithProgids` list.
4. **Trigger Windows Association Prompt:** The script automatically launches the native Windows dialog (`rundll32.exe shell32.dll,OpenAs_RunDLL "<file>"`) so you can select the handler once and check **"Always"**.

---

## 4. Alternative Future Implementations

To make the process 100% automated (no manual "Open With" confirmation click), here are possible directions to implement in the future:

### A. Integrating `SetUserFTA` (Recommended)
`SetUserFTA` is a popular command-line utility used by IT admins to bypass the `UserChoice` hash restriction.
* **How it works:** It reverse-engineers Microsoft's proprietary hash algorithm and writes both the association and the valid hash key to the registry.
* **Future Implementation:** Bundle `SetUserFTA.exe` in the script's `TOOLS` directory and run it via Python `subprocess`:
  ```python
  subprocess.run(['SetUserFTA.exe', '.json', 'Applications\\notepad++.exe'])
  ```

### B. Access Control List (ACL) Bypasses in PowerShell/C#
Create a small compiled helper binary or elevated PowerShell script that:
1. Takes registry ownership of the `UserChoice` registry key.
2. Strips the active **Deny** Access Control Entry (ACE) from the key's permissions.
3. Deletes the key, forcing Windows to fall back to the standard `HKCU\Software\Classes\.ext` file association configured by `editor_chooser.py`.

### C. Elevating via System-Wide `assoc`/`ftype`
If Administrator elevation is acceptable:
1. Ask the user for Admin privileges.
2. Run standard shell commands to override HKLM class associations:
   ```cmd
   assoc .json=Notepad++_document
   ftype Notepad++_document="C:\Program Files\Notepad++\notepad++.exe" "%1"
   ```
