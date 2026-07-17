#!/usr/bin/env python3
"""
install_deps.py — Parse a Python script and install only the third-party
imports that are actually used, via `uv pip install` into a dedicated
uv-managed Python environment.

Usage:
  1. CLI: python install_deps.py <script.py>
  2. Integration: Add this to the top of any script:
     import install_deps; install_deps.bootstrap(__file__, python_version="3.13", isolated=True)
     import install_deps; install_deps.bootstrap(__file__, isolated=False)
"""

import ast
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys


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

DEFAULT_PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
UV_ENV_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".uv-envs")


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


def resolve_pkg(module: str) -> str:
    return IMPORT_TO_PKG.get(module, module)


def resolve_python_version(python_version: str | None = None) -> str:
    return python_version or os.environ.get("INSTALL_DEPS_PYTHON_VERSION") or DEFAULT_PYTHON_VERSION


def ensure_uv_available() -> None:
    if shutil.which("uv") is None:
        raise RuntimeError("uv was not found on PATH. Install uv first, then rerun the script.")


def script_env_dir(script_path: str, python_version: str) -> str:
    script_path = os.path.abspath(script_path)
    digest = hashlib.sha256(script_path.encode("utf-8")).hexdigest()[:12]
    stem = os.path.splitext(os.path.basename(script_path))[0]
    safe_stem = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in stem)
    return os.path.join(UV_ENV_ROOT, f"{safe_stem}-{digest}-py{python_version}")


def venv_python_path(env_dir: str) -> str:
    if sys.platform == "win32":
        return os.path.join(env_dir, "Scripts", "python.exe")
    return os.path.join(env_dir, "bin", "python")


def python_version_matches(python_exe: str, expected: str) -> bool:
    try:
        result = subprocess.run(
            [
                python_exe,
                "-c",
                "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return False
    return result.stdout.strip() == expected


def ensure_target_python(script_path: str, python_version: str) -> str:
    ensure_uv_available()
    os.makedirs(UV_ENV_ROOT, exist_ok=True)

    env_dir = script_env_dir(script_path, python_version)
    python_exe = venv_python_path(env_dir)

    if not python_version_matches(python_exe, python_version):
        if os.path.isdir(env_dir):
            shutil.rmtree(env_dir)

        subprocess.run(["uv", "venv", "--python", python_version, env_dir], check=True)
        python_exe = venv_python_path(env_dir)

        if not os.path.exists(python_exe):
            raise RuntimeError(f"uv created {env_dir}, but {python_exe} was not found.")

    return python_exe


def probe_module_installed(python_exe: str, module: str) -> bool:
    check = VERIFY_SUBMODULE.get(module, module)
    try:
        result = subprocess.run(
            [
                python_exe,
                "-c",
                (
                    "import importlib.util, sys\n"
                    "try:\n"
                    "    spec = importlib.util.find_spec(sys.argv[1])\n"
                    "except Exception:\n"
                    "    spec = None\n"
                    "sys.exit(0 if spec is not None else 1)\n"
                ),
                check,
            ],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def has_local_module(script_dir: str, module: str) -> bool:
    return os.path.exists(os.path.join(script_dir, f"{module}.py")) or os.path.isdir(
        os.path.join(script_dir, module)
    )


def bootstrap(script_path: str, python_version: str | None = None, isolated: bool = True):
    """
    Call this at the top of a script to auto-install dependencies.
    Examples:
      import install_deps; install_deps.bootstrap(__file__, python_version="3.13", isolated=True)
      import install_deps; install_deps.bootstrap(__file__, isolated=False)
    """
    # Prevent infinite loops if a package fails to install
    if os.environ.get("INSTALL_DEPS_RESTARTED") == script_path:
        return

    script_path = os.path.abspath(script_path)
    script_dir = os.path.dirname(script_path)
    requested_python = resolve_python_version(python_version)
    if isolated:
        target_python = ensure_target_python(script_path, requested_python)
    else:
        target_python = sys.executable

    with open(script_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=script_path)

    imported = get_imported_names(tree)
    used_names = get_used_names(tree)
    third_party = {m for m in imported if m not in STDLIB and m != "install_deps"}

    installed_pkgs = []
    to_install = []
    for mod in sorted(third_party):
        if is_used(mod, tree, used_names):
            pkg = resolve_pkg(mod)
            if sys.platform != "win32" and pkg in {"pywin32", "windows-curses", "pywinpty"}:
                continue
            if has_local_module(script_dir, mod) or (
                isolated and probe_module_installed(target_python, mod)
            ) or (not isolated and is_installed(mod, script_dir)):
                installed_pkgs.append(pkg)
            else:
                to_install.append(pkg)

    if installed_pkgs:
        print(f"\n[+] Installed dependencies for {os.path.basename(script_path)}:")
        for pkg in installed_pkgs:
            print(f"  \033[92m- {pkg}\033[0m")

    if not to_install:
        if isolated and os.path.abspath(sys.executable) != os.path.abspath(target_python):
            env = os.environ.copy()
            utility_dir = os.path.dirname(os.path.abspath(__file__))
            env["PYTHONPATH"] = utility_dir + os.pathsep + env.get("PYTHONPATH", "")
            os.execve(target_python, [target_python, script_path] + sys.argv[1:], env)
        return

    print(f"\n[!] The following missing dependencies were detected for {os.path.basename(script_path)}:")
    for pkg in to_install:
        print(f"  \033[91m- {pkg}\033[0m")

    try:
        input("\nPress [ENTER] to proceed with installation via 'uv', or Ctrl+C to cancel...")
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user.")
        sys.exit(0)

    print("")
    if isolated:
        print(f"  using Python {requested_python} at: {target_python}")
        subprocess.run(["uv", "pip", "install", "--python", target_python, *to_install], check=True)
    else:
        print(f"  using current Python at: {target_python}")
        subprocess.run(["uv", "pip", "install", "--system", *to_install], check=True)

    if isolated:
        print("\n[!] Dependencies installed. Restarting script...\n")
        os.environ["INSTALL_DEPS_RESTARTED"] = script_path

        # Pass the current folder to PYTHONPATH so the restarted script can still find install_deps.py
        env = os.environ.copy()
        utility_dir = os.path.dirname(os.path.abspath(__file__))
        env["PYTHONPATH"] = utility_dir + os.pathsep + env.get("PYTHONPATH", "")

        os.execve(target_python, [target_python, script_path] + sys.argv[1:], env)
    else:
        print("\n[!] Dependencies installed into the current interpreter.\n")


def is_installed(module: str, script_dir: str = None) -> bool:
    if script_dir:
        if os.path.exists(os.path.join(script_dir, f"{module}.py")):
            return True
        if os.path.isdir(os.path.join(script_dir, module)):
            return True
    check = VERIFY_SUBMODULE.get(module, module)
    try:
        return importlib.util.find_spec(check) is not None
    except Exception:
        return False


def clean_unused_imports(script: str) -> None:
    with open(script, encoding="utf-8") as f:
        lines = f.readlines()
    tree = ast.parse("".join(lines))
    used_names = get_used_names(tree)

    unused_indices = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mod = (
                node.module.split(".")[0]
                if isinstance(node, ast.ImportFrom)
                else node.names[0].name.split(".")[0]
            )
            if mod in STDLIB:
                continue

            is_any_used = False
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname is None or alias.asname in used_names:
                        is_any_used = True
                        break
            else:
                for alias in node.names:
                    if (alias.asname or alias.name) == "*" or (alias.asname or alias.name) in used_names:
                        is_any_used = True
                        break

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
        print("Usage: install_deps.py <script.py> [--clean] [--python X.Y] [--system]")
        sys.exit(1)

    args = sys.argv[1:]
    python_version = None
    isolated = True
    if "--system" in args:
        isolated = False
        args.remove("--system")
    if "--python" in args:
        index = args.index("--python")
        try:
            python_version = args[index + 1]
        except IndexError:
            print("Error: --python requires a version like 3.13")
            sys.exit(2)
        del args[index:index + 2]
    else:
        for item in list(args):
            if item.startswith("--python="):
                python_version = item.split("=", 1)[1]
                args.remove(item)
                break

    if not args:
        print("Usage: install_deps.py <script.py> [--clean] [--python X.Y] [--system]")
        sys.exit(1)

    script = args[0]
    if "--clean" in args:
        clean_unused_imports(script)
    else:
        bootstrap(script, python_version=python_version, isolated=isolated)
        # If bootstrap returns, it means everything was already installed
        print(f"Running {script} ...\n")
        subprocess.run([sys.executable, script])


if __name__ == "__main__":
    main()
