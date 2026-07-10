import os
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Launch an isolated CLI environment for managing multiple accounts.")
    parser.add_argument("profile_name", help="The name of the profile to use or create (e.g., 'work', 'personal').")
    parser.add_argument("--shell", choices=["cmd", "pwsh", "powershell"], default="pwsh", help="The shell to launch (default: pwsh).")
    
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
    env["LOCALAPPDATA"] = str(appdata_local)
    env["HOME"] = str(profile_dir)
    env["XDG_CONFIG_HOME"] = str(appdata_roaming)
    env["XDG_DATA_HOME"] = str(appdata_local)
    
    # Isolate ProgramData in case tools try to do machine-wide saves
    programdata_dir = profile_dir / "ProgramData"
    programdata_dir.mkdir(parents=True, exist_ok=True)
    env["PROGRAMDATA"] = str(programdata_dir)
    env["ALLUSERSPROFILE"] = str(programdata_dir)
    
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
