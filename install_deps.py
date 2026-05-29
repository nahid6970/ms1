"""
install_deps.py — Parse a Python script and install only the third-party
imports that are actually used, via `uv pip install --system`.

Usage: python install_deps.py <script.py>
"""

import ast
import sys
import subprocess
import importlib.util

# stdlib modules (won't be installed)
STDLIB = sys.stdlib_module_names  # Python 3.10+

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
}


def get_imported_names(tree: ast.AST) -> set[str]:
    """Return top-level module names that appear in import statements."""
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
    """Return all Name/Attribute identifiers used in the code body."""
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            # collect root of attribute chains
            root = node
            while isinstance(root, ast.Attribute):
                root = root.value
            if isinstance(root, ast.Name):
                used.add(root.id)
    return used


def is_used(module: str, tree: ast.AST, used_names: set[str]) -> bool:
    """Check if a module is actually referenced in the code (not just imported)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == module:
                    # bare `import x` with no alias — treat as used (may have side effects)
                    if alias.asname is None:
                        return True
                    if alias.asname in used_names:
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


# For packages where top-level import succeeds but submodules may be missing,
# verify a known submodule instead.
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

def is_installed(module: str) -> bool:
    check = VERIFY_SUBMODULE.get(module, module)
    try:
        if importlib.util.find_spec(check) is None:
            return False
        __import__(check)
        return True
    except Exception:
        return False


def get_unused_import_lines(tree: ast.AST, used_names: set[str], source: str) -> set[int]:
    """Return 0-indexed line numbers of unused import statements."""
    unused_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod in STDLIB:
                    continue
                # bare import with no alias → always keep
                if alias.asname is None:
                    if mod not in used_names:
                        unused_lines.add(node.lineno - 1)
                else:
                    if alias.asname not in used_names:
                        unused_lines.add(node.lineno - 1)
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            all_unused = all(
                (alias.asname or alias.name) not in used_names and (alias.asname or alias.name) != "*"
                for alias in node.names
            )
            if all_unused:
                unused_lines.add(node.lineno - 1)
    return unused_lines


def clean_unused_imports(script: str, tree: ast.AST, used_names: set[str]) -> None:
    with open(script, encoding="utf-8") as f:
        lines = f.readlines()

    unused = get_unused_import_lines(tree, used_names, "".join(lines))
    if not unused:
        print("No unused imports to remove.")
        return

    new_lines = [l for i, l in enumerate(lines) if i not in unused]
    with open(script, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    for i in sorted(unused):
        print(f"  removed line {i+1}: {lines[i].rstrip()}")
    print(f"Removed {len(unused)} unused import(s).")


def main():
    if len(sys.argv) < 2:
        print("Usage: install_deps.py <script.py> [--clean] [--run]")
        sys.exit(1)

    script = sys.argv[1]
    clean = "--clean" in sys.argv
    run = True  # always run the script after

    with open(script, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=script)
    imported = get_imported_names(tree)
    used_names = get_used_names(tree)

    third_party = {m for m in imported if m not in STDLIB}

    if clean:
        clean_unused_imports(script, tree, used_names)
    else:
        to_install = []
        for mod in sorted(third_party):
            if not is_used(mod, tree, used_names):
                print(f"  skip (unused): {mod}")
                continue
            if is_installed(mod):
                print(f"  skip (present): {mod}")
                continue
            pkg = resolve_pkg(mod)
            to_install.append(pkg)

        to_install = sorted(set(to_install))

        if not to_install:
            print("Nothing to install.")
        else:
            print(f"\nInstalling: {', '.join(to_install)}")
            subprocess.run(["uv", "pip", "install", "--system"] + to_install, check=True)
            print("Done.")

    if run:
        print(f"\nRunning {script} ...\n")
        subprocess.run([sys.executable, script])


if __name__ == "__main__":
    main()
