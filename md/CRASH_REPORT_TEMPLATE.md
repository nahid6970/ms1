# Crash Reporting Template (Python / PyQt6)

The cleanest approach is a single shared `CrashLogger` class. Define it once, use it everywhere — no repeated `import traceback` or path lookups scattered through the code.

---

## The Logger Class

Put this near the top of your script, after imports:

```python
import sys, os, traceback, datetime

class CrashLogger:
    PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_report.txt")

    @classmethod
    def log(cls, label="CRASH", exc_info=None):
        with open(cls.PATH, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"{label} @ {datetime.datetime.now()}\n")
            if exc_info:
                f.write("".join(traceback.format_exception(*exc_info)))
            else:
                f.write(traceback.format_exc())
```

---

## 1. Main Thread — Global Exception Hook

```python
if __name__ == "__main__":

    def _excepthook(exc_type, exc_value, exc_tb):
        CrashLogger.log("CRASH", (exc_type, exc_value, exc_tb))
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _excepthook
```

---

## 2. QThread — Wrap run()

```python
class MyWorker(QThread):
    def run(self):
        try:
            # ... thread work ...
            pass
        except Exception:
            CrashLogger.log("THREAD CRASH")
```

---

## 3. subprocess with Timeout

```python
try:
    out, _ = p.communicate(timeout=15)
except subprocess.TimeoutExpired:
    p.kill()
    p.communicate()  # drain pipes
    return           # handle gracefully — emit [], show error, etc.
```

> Don't log TimeoutExpired as a crash — it's expected on slow networks. Just handle it silently.

---

## 4. QThread Signal Safety (PyQt6 specific)

When navigating away or replacing a running thread, always disconnect its signal first:

```python
if hasattr(self, "_worker") and self._worker.isRunning():
    self._worker.done.disconnect()  # prevent stale callback
    self._worker.stop()

self._worker = MyWorker(...)
self._worker.done.connect(self._on_done)
self._worker.start()
```

---

## Notes

- `crash_report.txt` is appended — all crashes accumulate with timestamps.
- `CrashLogger` resolves the path once from `__file__`, so it works regardless of working directory.
- Keep `sys.__excepthook__` call so the error still prints to console/stderr.
- `TimeoutExpired` is a subclass of `Exception` — if it's inside a bare `except Exception`, it will be caught and logged. Catch it explicitly first if you want to handle it silently.
