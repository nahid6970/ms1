# Quick Guide: Managing Python Versions & Packages with `uv`

This guide explains how to easily run scripts on older Python versions (like **Python 3.13**) when packages fail to install or compile on newer versions (like **Python 3.14**), without breaking your global system configuration.

---

## 💡 The Core Concept
* **The Problem:** Python 3.14 is too new for some packages (like `pyaudio`). They lack pre-built binaries (wheels), causing `uv pip install --system` to fail.
* **The Solution:** Use `uv run` with an inline script metadata block. This isolates the script, auto-downloads Python 3.13, and fetches dependencies seamlessly without changing your global system default (which stays 3.14).

---

## 🚀 Recommended Method: Self-Contained Scripts (Zero Boilerplate)

Instead of using a separate bootstrapper script, you can embed your Python requirements directly inside your script file as comments. `uv` handles the rest instantly using a fast, global package cache.

### Step 1: Format your Python Script (`my_script.py`)
Add this special comment block at the **very top** of your script:

```python
# /// script
# requires-python = "==3.13.*"
# dependencies = [
#     "pyaudio",
#     "opencv-python",
#     "Pillow",
# ]
# ///

import pyaudio
import cv2
from PIL import Image

print("Running flawlessly on Python 3.13 with all dependencies!")
```

### Step 2: Run the Script
Open your terminal and execute the script using `uv run`:
```bash
uv run my_script.py
```
*`uv` will automatically download Python 3.13 (if missing), spin up a temporary environment, install the packages, and run your script.*

---

## 🛠️ Pro-Tip: Let `uv` Create the Script Block For You

You don't need to write the `# /// script` metadata block manually. You can use terminal commands to inject it into any existing or new script:

1. **Initialize the script with a specific Python version:**
   ```bash
   uv add --script my_script.py --python 3.13
   ```
2. **Add packages to the script automatically:**
   ```bash
   uv add --script my_script.py pyaudio opencv-python Pillow
   ```

---

## ❓ Frequently Asked Questions

#### 1. Will this download packages fresh every single time?
**No.** `uv` uses a global, shared package cache on your computer. If multiple scripts use `Pillow` or `pyaudio`, `uv` downloads it exactly once. For subsequent scripts, it links the package from the cache in less than a millisecond.

#### 2. Will installing Python 3.13 via `uv` change my system default?
**No.** Your global default remains Python 3.14. Typing `python` or running other scripts normally will still use 3.14. `uv` installs its Python versions inside an isolated directory (`AppData\Local\uv\python` on Windows) where they won't conflict with anything else.

#### 3. How do I see what Python versions `uv` has access to?
Run this command in your terminal to see all available or downloaded versions:
```bash
uv python list
```
