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
    # Walk import nodes to find aliases
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] == module:
                    bound = alias.asname or alias.name.split(".")[0]
                    if bound in used_names:
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


def is_installed(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def main():
    if len(sys.argv) < 2:
        print("Usage: install_deps.py <script.py>")
        sys.exit(1)

    script = sys.argv[1]
    with open(script, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=script)
    imported = get_imported_names(tree)
    used_names = get_used_names(tree)

    third_party = {
        m for m in imported
        if m not in STDLIB and not is_used.__module__ == m  # keep logic clean
    }

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

    # deduplicate (e.g. multiple win32* → pywin32 once)
    to_install = sorted(set(to_install))

    if not to_install:
        print("Nothing to install.")
        return

    print(f"\nInstalling: {', '.join(to_install)}")
    subprocess.run(
        ["uv", "pip", "install", "--system"] + to_install,
        check=True,
    )
    print("Done.")


if __name__ == "__main__":
    main()
