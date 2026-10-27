"""Prepare the Reveal In Explorer host and open this extension in Chrome.

Run with: python run.py

The first Chrome setup still requires loading this folder as an unpacked
extension and enabling "Allow access to file URLs" in the extension details.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
INSTALLER = PROJECT_DIR / "reveal_explorer" / "install_host.py"
EXTENSIONS_URL = "chrome://extensions/"


def find_extension_ids() -> list[str]:
    """Find the ID Chrome assigned to this unpacked folder in its profiles."""
    chrome_data = Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "User Data"
    project_path = os.path.normcase(os.path.abspath(PROJECT_DIR))
    matches: set[str] = set()
    if not chrome_data.is_dir():
        raise RuntimeError(f"Chrome profile directory was not found: {chrome_data}")

    for profile_dir in chrome_data.iterdir():
        prefs_path = profile_dir / "Secure Preferences"
        if not profile_dir.is_dir() or not prefs_path.is_file():
            continue
        try:
            with prefs_path.open(encoding="utf-8") as prefs_file:
                settings = json.load(prefs_file).get("extensions", {}).get("settings", {})
        except (OSError, json.JSONDecodeError):
            continue

        for extension_id, details in settings.items():
            extension_path = details.get("path")
            if not extension_path:
                continue
            if os.path.normcase(os.path.abspath(extension_path)) == project_path:
                if len(extension_id) == 32 and all("a" <= c <= "p" for c in extension_id):
                    matches.add(extension_id)

    if not matches:
        raise RuntimeError(
            "Chrome has not loaded this exact folder as an unpacked extension. "
            f"In chrome://extensions, use Load unpacked and select: {PROJECT_DIR}"
        )
    return sorted(matches)


def register_native_host(extension_ids: list[str]) -> None:
    if os.name != "nt":
        raise RuntimeError("The Reveal In Explorer native host can only be registered on Windows.")
    subprocess.run([sys.executable, str(INSTALLER), *extension_ids], check=True, cwd=PROJECT_DIR)


def open_chrome_extensions() -> None:
    """Launch Chrome directly; Windows may not associate chrome:// links."""
    candidates = [
        shutil.which("chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                     "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                     "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""),
                     "Google", "Chrome", "Application", "chrome.exe"),
    ]
    chrome = next((candidate for candidate in candidates if candidate and os.path.isfile(candidate)), None)
    if not chrome:
        raise RuntimeError(
            "Could not find chrome.exe. Open Chrome manually and visit chrome://extensions/."
        )
    subprocess.Popen([chrome, EXTENSIONS_URL], cwd=PROJECT_DIR)


def main() -> int:
    try:
        extension_ids = find_extension_ids()
        register_native_host(extension_ids)
        open_chrome_extensions()
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"Setup failed: {error}", file=sys.stderr)
        return 1

    print("Native messaging host registered successfully for:")
    for extension_id in extension_ids:
        print(f"  chrome-extension://{extension_id}/")
    print(f"Project folder: {PROJECT_DIR}")
    print("In Chrome, load this folder with Load unpacked if you have not already,")
    print('then enable "Allow access to file URLs" in the extension details.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
