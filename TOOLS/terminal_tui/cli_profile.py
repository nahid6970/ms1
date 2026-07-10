import os
import argparse
import subprocess
from pathlib import Path

# Known browser executables (no user-data-dir override — uses default profile with all extensions)
BROWSER_PATHS = {
    "chrome": [
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
    ],
    "helium": [
        Path(os.environ.get("LOCALAPPDATA", "")) / "imput/Helium/Application/chrome.exe",
    ],
}

def launch_browser(browser: str):
    candidates = BROWSER_PATHS.get(browser.lower())
    if not candidates:
        print(f"Error: Unknown browser '{browser}'. Choose from: {', '.join(BROWSER_PATHS.keys())}")
        return

    exe = next((p for p in candidates if p.exists()), None)
    if not exe:
        print(f"Error: Could not find '{browser}' in known locations.")
        return

    print(f"  Launching {browser.capitalize()} with default profile...")
    # Launch detached so it doesn't block the shell session
    subprocess.Popen([str(exe)], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

def main():
    parser = argparse.ArgumentParser(description="Launch an isolated CLI environment for managing multiple accounts.")
    parser.add_argument("profile_name", help="The name of the profile to use or create (e.g., 'work', 'personal').")
    parser.add_argument("--shell", choices=["cmd", "pwsh", "powershell"], default="pwsh", help="The shell to launch (default: pwsh).")
    parser.add_argument("--browser", choices=list(BROWSER_PATHS.keys()), help="Also launch a browser using its default profile (no isolation).")
    parser.add_argument("--isolate-browser", action="store_true", help="Isolate the browser profile too (will force a clean browser session).")

    args = parser.parse_args()
    profile_name = args.profile_name

    # Define where the profiles will live. E.g. C:\Users\<User>\CLI_Profiles\<ProfileName>
    profiles_base_dir = Path.home() / "CLI_Profiles"
    profile_dir = profiles_base_dir / profile_name

    # Define AppData paths
    appdata_roaming = profile_dir / "AppData" / "Roaming"
    appdata_local = profile_dir / "AppData" / "Local"

    # Ensure directories exist
    appdata_roaming.mkdir(parents=True, exist_ok=True)
    appdata_local.mkdir(parents=True, exist_ok=True)

    print("==============================================")
    print(f"  Activated Isolated Profile: {profile_name}")
    print(f"  Profile Path: {profile_dir}")
    print("  CLI tool configurations will be saved here.")
    print("==============================================")

    # Prepare the new environment variables
    env = os.environ.copy()
    env["USERPROFILE"] = str(profile_dir)
    env["HOMEDRIVE"] = profile_dir.drive
    env["HOMEPATH"] = str(profile_dir)[len(profile_dir.drive):]
    env["APPDATA"] = str(appdata_roaming)
    env["HOME"] = str(profile_dir)
    env["XDG_CONFIG_HOME"] = str(appdata_roaming)
    
    # Ensure home directories for Codex and Gemini exist
    codex_home = profile_dir / ".codex"
    gemini_home = profile_dir / ".gemini"
    codex_home.mkdir(parents=True, exist_ok=True)
    gemini_home.mkdir(parents=True, exist_ok=True)
    
    env["CODEX_HOME"] = str(codex_home)
    env["GEMINI_HOME"] = str(gemini_home)

    if args.isolate_browser:
        env["LOCALAPPDATA"] = str(appdata_local)
        env["XDG_DATA_HOME"] = str(appdata_local)

    # Isolate ProgramData in case tools try to do machine-wide saves
    programdata_dir = profile_dir / "ProgramData"
    programdata_dir.mkdir(parents=True, exist_ok=True)
    env["PROGRAMDATA"] = str(programdata_dir)
    env["ALLUSERSPROFILE"] = str(programdata_dir)

    # Isolate Program Files folders
    programfiles_dir = profile_dir / "ProgramFiles"
    programfiles_dir.mkdir(parents=True, exist_ok=True)
    env["ProgramFiles"] = str(programfiles_dir)
    env["ProgramFiles(x86)"] = str(programfiles_dir)
    env["ProgramW6432"] = str(programfiles_dir)
    
    # Isolate Common Files folders
    commonfiles_dir = programfiles_dir / "Common"
    commonfiles_dir.mkdir(parents=True, exist_ok=True)
    env["CommonProgramFiles"] = str(commonfiles_dir)
    env["CommonProgramFiles(x86)"] = str(commonfiles_dir)
    env["CommonProgramW6432"] = str(commonfiles_dir)



    # Launch browser with its normal default profile (no isolation — keeps extensions like Bitwarden)
    if args.browser:
        launch_browser(args.browser)

    # Launch the specified shell
    try:
        if args.shell == "cmd":
            subprocess.run(["cmd.exe", "/k", f"title Profile: {profile_name}"], env=env, cwd=str(profile_dir))
        elif args.shell == "powershell":
            subprocess.run(["powershell.exe", "-NoExit", "-Command", f"$Host.UI.RawUI.WindowTitle = 'Profile: {profile_name}'"], env=env, cwd=str(profile_dir))
        else:
            subprocess.run(["pwsh.exe", "-NoExit", "-Command", f"$Host.UI.RawUI.WindowTitle = 'Profile: {profile_name}'"], env=env, cwd=str(profile_dir))
    except FileNotFoundError:
        print(f"Error: Could not find the shell '{args.shell}'. Is it installed?")

if __name__ == "__main__":
    main()
