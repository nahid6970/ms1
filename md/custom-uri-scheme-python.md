# Custom URI Scheme Handler (Python + Windows Registry)

Open local files and folders from any HTML page using a Python script registered as a custom protocol handler.

---

## How It Works

1. Register a custom protocol (e.g. `openfile:`, `opendir:`) in Windows Registry pointing to a Python script
2. In HTML/JS, navigate to `openfile:C:\path\to\file` 
3. Windows sees the protocol → launches the Python script with the URI as an argument
4. Python strips the protocol, decodes the path, and runs the action (`os.startfile`, `explorer.exe`, etc.)

No background process needed — Python is spawned on demand and exits immediately.

---

## Registry Structure

```
HKEY_CURRENT_USER\Software\Classes\<protocol>
  (Default) = "URL:<protocol> Protocol"
  URL Protocol = ""
  \shell\open\command
    (Default) = "C:\path\pythonw.exe" "C:\path\handler.py" "%1"
```

- `HKCU` = no admin required, only affects current user
- `pythonw.exe` = no console window flash
- `%1` = the full URI string passed as argument (e.g. `openfile:C:\my\file.txt`)

---

## Python Script Template

```python
import sys, os, subprocess, winreg
from urllib.parse import unquote

SCRIPT_PATH = os.path.abspath(__file__)
PYTHONW = sys.executable.replace("python.exe", "pythonw.exe").replace("python3.exe", "pythonw.exe")


def register(protocol):
    base = rf"Software\Classes\{protocol}"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base) as k:
        winreg.SetValueEx(k, "", 0, winreg.REG_SZ, f"URL:{protocol} Protocol")
        winreg.SetValueEx(k, "URL Protocol", 0, winreg.REG_SZ, "")
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{base}\shell\open\command") as k:
        winreg.SetValueEx(k, "", 0, winreg.REG_SZ, f'"{PYTHONW}" "{SCRIPT_PATH}" "%1"')
    print(f"Registered: {protocol}:")


def unregister(protocol):
    base = rf"Software\Classes\{protocol}"
    for sub in [r"\shell\open\command", r"\shell\open", r"\shell", ""]:
        try: winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base + sub)
        except FileNotFoundError: pass


def decode_path(uri, protocol):
    path = uri[len(protocol) + 1:].lstrip("/")  # strip "protocol:" and leading slashes
    return unquote(path).replace("/", "\\")      # decode %20 etc, normalize slashes


def open_file(uri):
    path = decode_path(uri, "openfile")
    if os.path.exists(path):
        os.startfile(path)  # opens with default app


def open_folder(uri):
    path = decode_path(uri, "opendir")
    target = path if os.path.exists(path) else os.path.dirname(path)
    if os.path.exists(target):
        subprocess.Popen(["explorer.exe", target])


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "--help"
    if arg == "--register":
        register("openfile")
        register("opendir")
    elif arg == "--unregister":
        unregister("openfile")
        unregister("opendir")
    elif arg.startswith("openfile:"):
        open_file(arg)
    elif arg.startswith("opendir:"):
        open_folder(arg)
```

---

## JS Usage

```js
// Open a file with its default app
window.location.href = 'openfile:C:\\projects\\report.pdf';

// Open a folder in Explorer
window.location.href = 'opendir:C:\\projects\\gallery';

// Convert file:/// URL to openfile:
function fileUrlToOpenfile(fileUrl) {
  return 'openfile:' + fileUrl.replace('file:///', '').replace(/\//g, '\\');
}
```

---

## Setup (once)

```bash
python handler.py --register
```

Chrome shows a one-time "Allow to open?" dialog — check **Always allow** and confirm.

---

## Other Actions You Can Trigger

| Action | Python code |
|--------|-------------|
| Open file with default app | `os.startfile(path)` |
| Open folder in Explorer | `subprocess.Popen(["explorer.exe", path])` |
| Open file in specific app | `subprocess.Popen(["notepad.exe", path])` |
| Run a script | `subprocess.Popen(["python.exe", "script.py", arg])` |
| Open URL in browser | `subprocess.Popen(["start", url], shell=True)` |
| Copy text to clipboard | `subprocess.run(["clip"], input=text.encode())` |

---

## Notes

- Re-running `--register` is safe (idempotent, just overwrites same keys)
- `HKCU` registration: no admin, only current user, no system-wide impact
- Custom protocol names can be anything not already used (`openfile`, `opendir`, `myapp`, etc.)
- Spaces in paths are handled automatically via `unquote()` (`%20` → space)
- The script file path is baked into the registry — don't move the script after registering (re-run `--register` if you do)
