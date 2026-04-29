"""
Kiro WSL Setup Script
Run this after a fresh WSL install to restore Kiro CLI configuration.
Usage: python3 setup.py
"""

import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")


def run(cmd, check=True):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print(f"    {result.stdout.strip()}")
    if result.returncode != 0 and check:
        print(f"  ERROR: {result.stderr.strip()}")
        sys.exit(1)
    return result


def step(msg):
    print(f"\n[+] {msg}")


# ── 1. Install kiro-cli ───────────────────────────────────────────────────────
step("Installing Kiro CLI")
result = run("which kiro 2>/dev/null || npm list -g kiro-cli 2>/dev/null", check=False)
if "kiro" in result.stdout:
    print("  Already installed, skipping.")
else:
    run("npm install -g @aws/kiro-cli")

# ── 2. Create ~/.kiro directories ────────────────────────────────────────────
step("Creating ~/.kiro directory structure")
for d in ["agents", "settings"]:
    os.makedirs(os.path.join(HOME, ".kiro", d), exist_ok=True)
    print(f"  Created ~/.kiro/{d}")

# ── 3. Copy agent config ──────────────────────────────────────────────────────
step("Installing agent config (stop hook for notifications)")
src = os.path.join(SCRIPT_DIR, "kiro_agents", "kiro_default.json")
dst = os.path.join(HOME, ".kiro", "agents", "kiro_default.json")
shutil.copy2(src, dst)
print(f"  Copied kiro_default.json → {dst}")

# ── 4. Verify Windows Python + PyQt6 accessible from WSL ─────────────────────
step("Checking Windows Python (python3.exe) and PyQt6")
r = run("python3.exe -c \"import PyQt6; print('PyQt6 OK')\" 2>&1", check=False)
if "PyQt6 OK" in r.stdout:
    print("  PyQt6 available on Windows Python ✓")
else:
    print("  PyQt6 not found — installing on Windows Python...")
    run("python3.exe -m pip install PyQt6")

# ── 5. Verify notification script exists on Windows side ─────────────────────
step("Verifying notification script")
notify_path = r"C:\@delta\ms1\asset\kiro\task_complete.py"
wsl_path = "/mnt/c/@delta/ms1/asset/kiro/task_complete.py"
if os.path.exists(wsl_path):
    print(f"  Found: {wsl_path} ✓")
else:
    print(f"  Not found at {wsl_path} — copying from setup folder...")
    os.makedirs("/mnt/c/@delta/ms1/asset/kiro", exist_ok=True)
    shutil.copy2(os.path.join(SCRIPT_DIR, "task_complete.py"), wsl_path)
    print(f"  Copied task_complete.py → {wsl_path}")

# ── 6. Quick smoke test ───────────────────────────────────────────────────────
step("Running notification popup (close it to continue)")
run(f"python3.exe '{notify_path}' &", check=False)

print("\n✅ Kiro WSL setup complete!\n")
print("   Start Kiro with: kiro")
print("   Notification fires automatically after each completed task.\n")
