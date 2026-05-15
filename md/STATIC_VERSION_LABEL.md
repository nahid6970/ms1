# Static Version Label Pattern

A dead-simple way to know if GitHub Pages (or any static host) is serving a cached old version.

## The Problem

GitHub Pages can take 1–5 minutes to deploy after a push. During that time, you might be looking at the old cached page without knowing it.

## The Solution

Embed a visible version label directly in your HTML. Change it manually with every push. If the label on the live site doesn't match what you just pushed, the page is still stale.

---

## Implementation

### 1. Add the label to your HTML

Place it somewhere always visible — e.g. a topbar or footer:

```html
<div id="version-badge" style="background:#555;color:#ccc;padding:3px 8px;border-radius:4px;font-size:11px;">v1</div>
```

### 2. Change the text before every push

Just edit `v1` → `v2` → `T3` → whatever. Any change works.

```html
<div id="version-badge" ...>v2</div>
```

### 3. After pushing, check the live site

- Label shows `v2` → deployment is live ✅  
- Label still shows `v1` → GitHub Pages hasn't updated yet, wait and refresh ⏳

---

## Optional: Python GUI to change it without opening a text editor

If you don't want to manually open the HTML file each time, use a small PyQt6 script:

```python
import sys, re, os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel

HTML_FILE = os.path.join(os.path.dirname(__file__), "index.html")
PATTERN = re.compile(r'(<div id="version-badge"[^>]*>)([^<]*)(</div>)')

def read_current():
    with open(HTML_FILE, encoding="utf-8") as f: content = f.read()
    m = PATTERN.search(content)
    return m.group(2).strip() if m else ""

def write_version(text):
    with open(HTML_FILE, encoding="utf-8") as f: content = f.read()
    new, n = PATTERN.subn(lambda m: m.group(1) + text + m.group(3), content)
    if n: open(HTML_FILE, "w", encoding="utf-8").write(new)
    return bool(n)

app = QApplication(sys.argv)
w = QWidget(); w.setWindowTitle("Set Version"); w.resize(300, 90)
layout = QVBoxLayout(w)
inp = QLineEdit(read_current()); layout.addWidget(inp)
status = QLabel(""); layout.addWidget(status)
btn = QPushButton("Save")
btn.clicked.connect(lambda: status.setText("Saved ✓" if write_version(inp.text().strip()) else "Error ✗"))
layout.addWidget(btn)
w.show(); sys.exit(app.exec())
```

---

## Tips

- Keep the label short: `v1`, `v2`, `T1`, `fix1`, date like `0515` — anything you'll recognize.
- Put it somewhere you always see it (topbar, bottom corner).
- No build tools, no CI, no scripts required — just a text change.
- Works for any static site: GitHub Pages, Netlify, Vercel, S3, etc.
