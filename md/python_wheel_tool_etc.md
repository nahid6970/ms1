# Quick Guide: Updating Python Development Tools with `uv`

When you switch from traditional `pip` to `uv`, the way you manage and update development tools changes. Because `uv` is a compiled tool written in Rust, it automates or replaces many old-school maintenance tasks (like constantly updating `wheel`).

---

## 🚀 1. How to Update `uv` Itself (Most Important)
`uv` receives frequent updates with speed improvements and better compatibility for new Python versions. Keep it updated to avoid environment bugs.

Run the command that matches how you originally installed it:
* **Standalone Installer (Recommended):**
  ```bash
  uv self update
  ```
* **Via Traditional Pip:**
  ```bash
  pip install --upgrade uv
  ```
* **Via Homebrew (macOS):**
  ```bash
  brew upgrade uv
  ```

---

## 🛠️ 2. Updating Core Build Tools (`wheel`, `setuptools`, `pip`)

### The New Way (`uv run` / Virtual Environments)
**You do not need to manually update these.** 
When `uv` builds a package from source, it automatically fetches the latest required build tools in an isolated sandbox behind the scenes. You can stop typing `python -m pip install --upgrade pip wheel`.

If a legacy script specifically requires `wheel` to be present in your environment, upgrade it like any standard library:
```bash
uv pip install --upgrade wheel setuptools --system
```

### The Old Way (Global System Python 3.14)
If you still run global scripts outside of `uv` and need to update your system's core Python tools, use the standard python executable:
```bash
python -m pip install --upgrade pip setuptools wheel
```

---

## 🧰 3. Managing Global CLI Tools (`uv tool`)
If you use standalone Python applications (like `ruff`, `black`, `flake8`, or `yt-dlp`), stop installing them globally with `pip`. Use `uv tool` to install them in isolated, auto-managed bubbles.

* **Install a tool:**
  ```bash
  uv tool install ruff
  ```
* **Upgrade a specific tool:**
  ```bash
  uv tool upgrade ruff
  ```
* **Upgrade ALL installed tools at once:**
  ```bash
  uv tool upgrade --all
  ```

---

## 🧹 4. Cleaning Up the Cache
Since `uv` caches packages globally to save time and internet bandwidth, the cache can grow over time. You can safely clear out old, unused versions of packages and Python toolchains with one command:

```bash
uv cache clean
```
