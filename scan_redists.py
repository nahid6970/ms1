"""
scan_redists.py — Scans the Windows Registry to list installed 
Microsoft Visual C++ Redistributables.
"""

import winreg
import re

def get_installed_redists():
    print("Searching for installed Microsoft Visual C++ Redistributables...\n")
    
    # Common registry paths for "Add/Remove Programs"
    paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    found_versions = []
    
    for path in paths:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if "Microsoft Visual C++" in display_name and "Redistributable" in display_name:
                                    # Use regex to clean up the name for readability
                                    clean_name = re.sub(r"\(x64\)|\(x86\)", "", display_name).strip()
                                    arch = "x64" if "x64" in display_name else "x86"
                                    found_versions.append(f"- {display_name}")
                            except EnvironmentError:
                                continue
                    except EnvironmentError:
                        continue
        except EnvironmentError:
            continue

    if not found_versions:
        print("No Redistributables detected in the standard registry paths.")
    else:
        # Deduplicate and sort
        for item in sorted(set(found_versions)):
            print(item)

def main():
    import os
    if os.name != 'nt':
        print("This script only works on Windows.")
        return

    get_installed_redists()
    
    print("\n--- Note on Python 3.14 and pyaudio ---")
    print("If you are trying to fix the 'pyaudio' build error:")
    print("Installing these Redistributables will NOT fix the error.")
    print("You specifically need the 'C++ Build Tools' (Compiler) to install packages")
    print("on experimental Python versions like 3.14.")

if __name__ == "__main__":
    main()
