# Self-contained Python dependency setup

Use this guide when updating a Python script so it can still be launched directly:

```powershell
python path\to\script.py
```

The script must install missing dependencies into the exact Python interpreter that launched it. Do not require the user to remember `uv run`, a separate requirements file, or a project-specific command.

## Required implementation

Place the following in the target script:

1. A module docstring, if needed.
2. Any `from __future__ import ...` lines immediately after the docstring.
3. Inline PEP 723 dependency metadata.
4. Standard-library imports and the bootstrap function.
5. The call to the bootstrap function.
6. Third-party imports.

Example:

```python
"""Application description."""
from __future__ import annotations

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "Pillow",
#     "PyQt6",
#     "pywin32",
# ]
# ///

import importlib.util
import shutil
import subprocess
import sys

DEPENDENCIES = (
    ("PIL", "Pillow"),
    ("PyQt6", "PyQt6"),
    ("win32clipboard", "pywin32"),
)


def ensure_dependencies():
    missing = [
        package
        for module, package in DEPENDENCIES
        if importlib.util.find_spec(module) is None
    ]
    if not missing:
        return

    uv = shutil.which("uv")
    if uv:
        command = [uv, "pip", "install", "--python", sys.executable, *missing]
    else:
        command = [sys.executable, "-m", "pip", "install", *missing]
    subprocess.check_call(command)


ensure_dependencies()

from PIL import Image
```

## Import-name to package-name rules

Never assume the import name is the package name. Use explicit mappings in `DEPENDENCIES`:

| Import used by code | Package to install |
| --- | --- |
| `PIL` | `Pillow` |
| `cv2` | `opencv-python` |
| `yaml` | `PyYAML` |
| `bs4` | `beautifulsoup4` |
| `dateutil` | `python-dateutil` |
| `jwt` | `PyJWT` |
| `fitz` | `PyMuPDF` |
| `skimage` | `scikit-image` |
| `win32api`, `win32com`, `win32gui`, `win32clipboard` | `pywin32` |
| `flask` | `Flask` |
| `flask_sqlalchemy` | `Flask-SQLAlchemy` |
| `flask_socketio` | `Flask-SocketIO` |
| `flask_cors` | `Flask-Cors` |
| `flask_login` | `Flask-Login` |
| `socketio` | `python-socketio` |
| `nacl` | `PyNaCl` |

Add an explicit tuple whenever a script uses another mismatched import. Include every top-level module that is imported, including optional or lazy imports.

## Optional dependencies

If a feature is optional, do not install its heavy dependency during startup. Use a separate function that installs/checks it only when the feature is selected. For example, OCR packages such as `easyocr` can be deferred until the OCR action is used.

## Rules for updating a script

- Preserve the script's existing behavior and command-line interface.
- Do not place executable imports before `from __future__ import ...`.
- Do not import third-party modules before `ensure_dependencies()` runs.
- Always use `sys.executable`; never use bare `pip` or a hard-coded Python path.
- Prefer `uv pip install --python sys.executable` when `uv` exists.
- Fall back to `sys.executable -m pip` when `uv` is unavailable.
- Do not install packages while validating the edit.
- Run syntax validation with `python -m py_compile script.py`.
- Parse the file with `ast.parse` and verify that the dependency bootstrap is before third-party imports.
- If a dependency is already installed, do nothing.
- If installation fails, show the package names and the exact interpreter path in the error.
- Do not catch and hide real application errors after dependency setup.

## Important limitation

Missing-module errors can be fixed automatically, but arbitrary runtime crashes cannot. Python also cannot reliably infer the PyPI package name for every import. Explicit dependency declarations are therefore preferred over scanning imports and guessing package names.
