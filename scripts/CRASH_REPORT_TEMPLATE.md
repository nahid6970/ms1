# Crash Reporting Template (Python / PyQt6)

Add this to any Python script to automatically log crashes to a `crash_report.txt` in the script's directory.

---

## 1. Global Exception Hook (main thread crashes)

Add at the top of your `if __name__ == "__main__":` block:

```python
if __name__ == "__main__":
    import traceback, datetime

    CRASH_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_report.txt")

    def _excepthook(exc_type, exc_value, exc_tb):
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"CRASH @ {datetime.datetime.now()}\n")
            f.write("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _excepthook
```

---

## 2. QThread Crash Logging (background thread crashes)

Wrap your `QThread.run()` method:

```python
def run(self):
    try:
        # ... your thread code ...
        pass
    except Exception:
        import traceback, datetime
        _log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_report.txt")
        with open(_log, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"THREAD CRASH @ {datetime.datetime.now()}\n")
            f.write(traceback.format_exc())
```

---

## 3. subprocess.TimeoutExpired (rclone / subprocess calls)

When using `subprocess` with a timeout, handle `TimeoutExpired` explicitly to avoid a silent crash:

```python
try:
    out, _ = p.communicate(timeout=15)
except subprocess.TimeoutExpired:
    p.kill()
    p.communicate()  # drain pipes
    # handle gracefully (return empty, show error, etc.)
    return
```

---

## Notes

- `crash_report.txt` is appended, not overwritten — all crashes accumulate.
- Each entry is separated by `====` and timestamped.
- For PyQt6 signals: always disconnect signals from a thread before stopping it to prevent stale signal callbacks firing after the thread is replaced.
