# Isolated CLI Profile Switcher

This script (`cli_profile.py`) allows you to run CLI tools (such as Gemini, Codex CLI, Kiro CLI, etc.) with multiple isolated accounts on the same Windows machine. It achieves complete session isolation by launching a nested terminal session with redirected directories (`USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, `HOME`, `PROGRAMDATA`, etc.).

---

## How It Works

When you run the script with a profile name:
1. It creates an isolated profile folder inside `C:\Users\<YourUsername>\CLI_Profiles\<profile_name>`.
2. It overrides environment variables for the shell session:
   - `USERPROFILE`, `HOME`, `HOMEDRIVE`, `HOMEPATH`
   - `APPDATA`, `LOCALAPPDATA`
   - `XDG_CONFIG_HOME`, `XDG_DATA_HOME`
   - `PROGRAMDATA`, `ALLUSERSPROFILE`
3. It starts a new shell inside that directory. Any tool executed within this shell will save its authentication tokens and configuration files exclusively inside the isolated profile directory.

---

## Usage

### 1. Basic Switch (PowerShell)
By default, the script launches inside Windows PowerShell Core (`pwsh`).
```powershell
python cli_profile.py <profile_name>
```

**Example:**
```powershell
python cli_profile.py work
```
This opens a new terminal window locked to the `work` profile context. Run your login commands here (e.g. `codex login`), and they will be isolated to the `work` folder.

To switch to a different account, open a new terminal window and run:
```powershell
python cli_profile.py personal
```

### 2. Choosing a Shell (`--shell`)
You can specify which shell you want to launch using the `--shell` flag:

- **Command Prompt (CMD):**
  ```powershell
  python cli_profile.py work --shell cmd
  ```
- **Windows PowerShell:**
  ```powershell
  python cli_profile.py work --shell powershell
  ```
- **PowerShell Core (Default):**
  ```powershell
  python cli_profile.py work --shell pwsh
  ```

### 3. Isolating the Browser (`--isolate-browser`)
By default, browsers triggered by your CLI tools (like login URLs) will launch using your default browser settings so that extensions (like Bitwarden) and saved logins remain available. 

If you want to force a completely clean, isolated browser session (e.g. to test a clean sign-up flow), add the `--isolate-browser` flag:
```powershell
python cli_profile.py work --isolate-browser
```

---

## Where Are My Files Saved?

All profile files (configurations, local cache, login tokens) are saved under your user home directory:
```
C:\Users\<YourUsername>\CLI_Profiles\<profile_name>\
```
Inside this folder, you will see subfolders like `AppData` and `ProgramData` capturing any files that would normally be saved globally on your PC.
