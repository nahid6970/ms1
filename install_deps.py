#!/usr/bin/env python3
"""
install_deps.py — Parse a Python script and install only the third-party
imports that are actually used, via `uv pip install --system`.

Usage: 
  1. CLI: python install_deps.py <script.py>
  2. Integration: Add this to the top of any script:
     import install_deps; install_deps.bootstrap(__file__)
"""

import ast
import sys
import os
import subprocess
import importlib.util

# stdlib modules (won't be installed)
STDLIB = sys.stdlib_module_names - ({"curses"} if sys.platform == "win32" else set())

# map import name → pip package name when they differ
IMPORT_TO_PKG = {
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "sklearn": "scikit-learn",
    "bs4": "beautifulsoup4",
    "yaml": "PyYAML",
    "dotenv": "python-dotenv",
    "wx": "wxPython",
    "gi": "PyGObject",
    "usb": "pyusb",
    "serial": "pyserial",
    "speech_recognition": "SpeechRecognition",
    "curses": "windows-curses",
    "Cryptodome": "pycryptodomex",
    "Crypto": "pycryptodome",
    "pyadl": "pyadl",
    "win32api": "pywin32",
    "win32con": "pywin32",
    "win32gui": "pywin32",
    "win32process": "pywin32",
    "pywintypes": "pywin32",
    "winerror": "pywin32",
    "PyQt6": "PyQt6",
    "psutil": "psutil",
    "winpty": "pywinpty",
}

VERIFY_SUBMODULE = {
    "PyQt6": "PyQt6.QtWidgets",
    "PyQt5": "PyQt5.QtWidgets",
    "PySide6": "PySide6.QtWidgets",
    "PySide2": "PySide2.QtWidgets",
    "PIL": "PIL.Image",
    "sklearn": "sklearn.utils",
    "scipy": "scipy.linalg",
    "numpy": "numpy.core",
}

def get_imported_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0])
    return names

def get_used_names(tree: ast.AST) -> set[str]:
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            root = node
            while isinstance(root, ast.Attribute):
                root = root.value
            if isinstance(root, ast.Name):
                used.add(root.id)
    return used

def is_used(module: str, tree: ast.AST, used_names: set[str]) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == module:
                    if alias.asname is None or alias.asname in used_names:
                        return True
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] == module:
                for alias in node.names:
                    bound = alias.asname or alias.name
                    if bound == "*" or bound in used_names:
                        return True
    return False

def is_installed(module: str, script_dir: str = None) -> bool:
    if script_dir:
        if os.path.exists(os.path.join(script_dir, f"{module}.py")): return True
        if os.path.isdir(os.path.join(script_dir, module)): return True
    check = VERIFY_SUBMODULE.get(module, module)
    try:
        return importlib.util.find_spec(check) is not None
    except Exception:
        return False

def resolve_pkg(module: str) -> str:
    return IMPORT_TO_PKG.get(module, module)

def bootstrap(script_path: str):
    """
    Call this at the top of a script to auto-install dependencies.
    Example: import install_deps; install_deps.bootstrap(__file__)
    """
    # Prevent infinite loops if a package fails to install
    if os.environ.get("INSTALL_DEPS_RESTARTED") == script_path:
        return

    script_path = os.path.abspath(script_path)
    script_dir = os.path.dirname(script_path)

    with open(script_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=script_path)

    imported = get_imported_names(tree)
    used_names = get_used_names(tree)
    third_party = {m for m in imported if m not in STDLIB}
    
    to_install = []
    for mod in sorted(third_party):
        if is_used(mod, tree, used_names) and not is_installed(mod, script_dir):
            pkg = resolve_pkg(mod)
            if sys.platform != "win32" and pkg in {"pywin32", "windows-curses", "pywinpty"}:
                continue
            to_install.append(pkg)

    if not to_install:
        return

    print(f"\n[!] The following missing dependencies were detected for {os.path.basename(script_path)}:")
    for pkg in to_install:
        print(f"  - {pkg}")
    
    try:
        input("\nPress [ENTER] to proceed with installation via 'uv', or Ctrl+C to cancel...")
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user.")
        sys.exit(0)

    print("")
    for pkg in to_install:
        print(f"  installing {pkg}...")
        subprocess.run(["uv", "pip", "install", "--system", pkg])

    print("\n[!] Dependencies installed. Restarting script...\n")
    os.environ["INSTALL_DEPS_RESTARTED"] = script_path
    
    # Pass the current folder to PYTHONPATH so the restarted script can still find install_deps.py
    env = os.environ.copy()
    utility_dir = os.path.dirname(os.path.abspath(__file__))
    env["PYTHONPATH"] = utility_dir + os.pathsep + env.get("PYTHONPATH", "")
    
    os.execve(sys.executable, [sys.executable, script_path] + sys.argv[1:], env)

def clean_unused_imports(script: str) -> None:
    with open(script, encoding="utf-8") as f:
        lines = f.readlines()
    tree = ast.parse("".join(lines))
    used_names = get_used_names(tree)
    
    unused_indices = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mod = (node.module.split(".")[0] if isinstance(node, ast.ImportFrom) else node.names[0].name.split(".")[0])
            if mod in STDLIB: continue
            
            is_any_used = False
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname is None or alias.asname in used_names:
                        is_any_used = True; break
            else:
                for alias in node.names:
                    if (alias.asname or alias.name) == "*" or (alias.asname or alias.name) in used_names:
                        is_any_used = True; break
            
            if not is_any_used:
                unused_indices.append(node.lineno - 1)

    if not unused_indices:
        print("No unused imports to remove.")
        return

    new_lines = [l for i, l in enumerate(lines) if i not in unused_indices]
    with open(script, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Removed {len(unused_indices)} unused import(s).")

def main():
    if len(sys.argv) < 2:
        print("Usage: install_deps.py <script.py> [--clean]")
        sys.exit(1)

    script = sys.argv[1]
    if "--clean" in sys.argv:
        clean_unused_imports(script)
    else:
        bootstrap(script)
        # If bootstrap returns, it means everything was already installed
        print(f"Running {script} ...\n")
        subprocess.run([sys.executable, script])

if __name__ == "__main__":
    main()
