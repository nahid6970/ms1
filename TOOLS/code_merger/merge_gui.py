import sys
import os
import re
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QGroupBox,
    QFileDialog, QListWidget, QListWidgetItem, QSplitter,
    QStatusBar, QCheckBox, QMessageBox, QLineEdit, QMenu, QFrame,
    QDialog, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QFont, QColor

# ── PALETTE ──────────────────────────────────────────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"
CP_SUB    = "#808080"

THEME = f"""
QMainWindow, QDialog {{ background-color: {CP_BG}; }}
QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; background-color: {CP_BG}; }}
QTabWidget::pane {{ border: 1px solid {CP_DIM}; background: {CP_BG}; }}
QTabBar::tab {{ background: {CP_PANEL}; color: {CP_SUB}; padding: 6px 18px; border: 1px solid {CP_DIM}; border-bottom: none; }}
QTabBar::tab:selected {{ background: {CP_BG}; color: {CP_YELLOW}; border-bottom: 2px solid {CP_YELLOW}; }}
QTabBar::tab:hover {{ color: {CP_CYAN}; }}
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
    selection-background-color: {CP_CYAN}; selection-color: #000;
}}
QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {CP_CYAN}; }}
QPushButton {{
    background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white;
    padding: 6px 14px; font-weight: bold;
}}
QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
QGroupBox {{
    border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px;
    font-weight: bold; color: {CP_YELLOW};
}}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
QListWidget {{
    background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM};
    alternate-background-color: #1a1a1a;
}}
QListWidget::item:selected {{ background-color: #1a3a3a; color: {CP_CYAN}; border-left: 2px solid {CP_CYAN}; }}
QListWidget::item:hover {{ background-color: #1a1a1a; }}
QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 5px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; background: none; }}
QScrollBar:horizontal {{ background: {CP_BG}; height: 10px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {CP_CYAN}; min-width: 20px; border-radius: 5px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; background: none; }}
QCheckBox {{ spacing: 8px; color: {CP_TEXT}; background: transparent; }}
QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
QSplitter::handle {{ background: {CP_DIM}; }}
QStatusBar {{ background: {CP_PANEL}; color: {CP_SUB}; border-top: 1px solid {CP_DIM}; }}
"""

_HERE        = os.path.dirname(os.path.abspath(__file__))
GUIDE_PATH   = os.path.join(_HERE, "PROMPT_GUIDE.md")
RECENT_PATH  = os.path.join(_HERE, "recent_projects.json")
SESSION_PATH = os.path.join(_HERE, "session.json")
MAX_RECENT   = 8

IGNORE_PATTERNS = {
    '__pycache__', '.git', '.venv', 'venv', 'node_modules', '.idea', '.vscode',
    'dist', 'build', '.mypy_cache', '.pytest_cache', '.next', '.nuxt', 'out', 
    'coverage', '.DS_Store', 'Thumbs.db'
}
IGNORE_EXTS = {
    # Compiled / Binaries
    '.pyc', '.pyo', '.pyd', '.exe', '.dll', '.so', '.egg', '.db', '.lock', 
    '.class', '.jar', '.war', '.sqlite', '.sqlite3',
    # Images / Graphics
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp', '.bmp', '.tiff',
    # Audio / Video
    '.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mkv', '.mov', '.webm',
    # Compressed Archives
    '.zip', '.tar', '.gz', '.rar', '.7z',
    # Documents
    '.pdf', '.docx', '.xlsx', '.pptx',
    # Fonts
    '.ttf', '.otf', '.woff', '.woff2', '.eot'
}

CUSTOM_IGNORED_EXTS = set()

def load_custom_ignores():
    global CUSTOM_IGNORED_EXTS
    import json
    try:
        if os.path.exists(SESSION_PATH):
            with open(SESSION_PATH, 'r') as f:
                data = json.load(f)
            ignores = data.get('custom_ignored_exts', [])
            CUSTOM_IGNORED_EXTS = set(ignores)
            IGNORE_EXTS.update(CUSTOM_IGNORED_EXTS)
    except Exception:
        pass

def save_custom_ignores(ignores: list[str]):
    global CUSTOM_IGNORED_EXTS
    import json
    CUSTOM_IGNORED_EXTS = set(ignores)
    IGNORE_EXTS.update(CUSTOM_IGNORED_EXTS)
    try:
        data = {}
        if os.path.exists(SESSION_PATH):
            with open(SESSION_PATH, 'r') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {}
        data['custom_ignored_exts'] = list(CUSTOM_IGNORED_EXTS)
        with open(SESSION_PATH, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def load_recent() -> list[str]:
    try:
        import json
        with open(RECENT_PATH, 'r') as f:
            raw = json.load(f)
        seen, out = set(), []
        for item in raw:
            if isinstance(item, dict):
                p = item.get("path")
            else:
                p = item
            if not p:
                continue
            n = os.path.normpath(p)
            if n not in seen:
                seen.add(n)
                out.append(n)
        return out
    except Exception:
        return []

def load_recent_details() -> list[dict]:
    try:
        import json
        with open(RECENT_PATH, 'r') as f:
            raw = json.load(f)
        out = []
        seen = set()
        for item in raw:
            if isinstance(item, dict):
                p = item.get("path")
                files = item.get("files", [])
                extensions = item.get("extensions", [])
            else:
                p = item
                files = []
                extensions = []
            if not p:
                continue
            n = os.path.normpath(p)
            if n not in seen:
                seen.add(n)
                out.append({"path": n, "files": files, "extensions": extensions})
        return out
    except Exception:
        return []

def save_recent(items: list[dict]):
    import json
    with open(RECENT_PATH, 'w') as f:
        json.dump(items, f, indent=2)

def add_recent(path: str, files: list[str] = None, extensions: list[str] = None, overwrite_existing: bool = False):
    path = os.path.normpath(path)

    current = load_recent_details()
    
    # Locate existing entry to avoid overwriting previously stored selection details
    existing = None
    for item in current:
        if os.path.normpath(item["path"]) == path:
            existing = item
            break

    # If overwrite_existing is False, preserve any existing saved selection details
    if not overwrite_existing and existing:
        if existing.get("files"):
            files = existing["files"]
        if existing.get("extensions"):
            extensions = existing["extensions"]
    else:
        # Fallback if none provided
        if not files:
            if existing and existing.get("files"):
                files = existing["files"]
        if not extensions:
            if existing and existing.get("extensions"):
                extensions = existing["extensions"]

    if files is None:
        files = []
    if extensions is None:
        extensions = []

    normalized_files = [os.path.normpath(f) for f in files]

    # Remove existing entry to move it to the top of the list
    current = [item for item in current if os.path.normpath(item["path"]) != path]
    current.insert(0, {
        "path": path,
        "files": normalized_files,
        "extensions": extensions
    })
    save_recent(current[:MAX_RECENT])

def remove_recent(path: str):
    path = os.path.normpath(path)
    current = load_recent_details()
    current = [item for item in current if os.path.normpath(item["path"]) != path]
    save_recent(current)

# ── MERGE LOGIC ───────────────────────────────────────────────────────────────
_TOKENS = r'(@@FILE:|@@MODE:|@@TO:|@@FROM:|@@AFTER:|@@INSERT:|@@END)'

def _normalize(text: str) -> str:
    """Normalize AI response: strip markdown fences, ensure @@ tokens are on their own lines."""
    # 1. Strip markdown code fences (```lang ... ```) wrapping the whole response or blocks
    text = re.sub(r'^```[^\n]*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'^```$', '', text, flags=re.MULTILINE)
    # 2. Insert newline before any @@ token not already at start of line
    text = re.sub(r'(?<!\n)(@@(?:FILE|MODE|TO|FROM|AFTER|INSERT|END)\b:?)', r'\n\1', text)
    # 3. Move inline content after content-bearing tokens to the next line
    #    e.g. "@@TO: some code" → "@@TO:\nsome code"
    text = re.sub(r'^(@@(?:TO|FROM|AFTER|INSERT):) *(.+)$', r'\1\n\2', text, flags=re.MULTILINE)
    return text


def parse_ai_response(text: str) -> list[dict]:
    """Parse AI response into list of change dicts. Handles inline and multi-line formats."""
    text = _normalize(text)
    changes = []
    parts = re.split(r'(?=@@FILE:)', text)
    for part in parts:
        part = part.strip()
        if not part.startswith("@@FILE:"):
            continue
        lines = part.split('\n')
        filepath = lines[0].replace("@@FILE:", "").strip()
        body = '\n'.join(lines[1:])

        mode_m = re.search(r'@@MODE:\s*(\w+)', body)
        mode = mode_m.group(1) if mode_m else "replace_block"

        if mode == "replace_file":
            to_m = re.search(r'@@TO:\n(.*?)@@END', body, re.DOTALL)
            if to_m:
                changes.append({"file": filepath, "mode": mode, "to": to_m.group(1)})

        elif mode == "replace_block":
            from_m = re.search(r'@@FROM:\n(.*?)@@TO:', body, re.DOTALL)
            to_m   = re.search(r'@@TO:\n(.*?)@@END', body, re.DOTALL)
            if from_m and to_m:
                changes.append({"file": filepath, "mode": mode,
                                 "from": from_m.group(1), "to": to_m.group(1)})

        elif mode == "insert_after":
            after_m  = re.search(r'@@AFTER:\n(.*?)@@INSERT:', body, re.DOTALL)
            insert_m = re.search(r'@@INSERT:\n(.*?)@@END', body, re.DOTALL)
            if after_m and insert_m:
                changes.append({"file": filepath, "mode": mode,
                                 "after": after_m.group(1).rstrip('\n'),
                                 "insert": insert_m.group(1)})

        elif mode == "delete_block":
            from_m = re.search(r'@@FROM:\n(.*?)@@END', body, re.DOTALL)
            if from_m:
                changes.append({"file": filepath, "mode": mode, "from": from_m.group(1)})

    return changes


def apply_changes(changes: list[dict], root: str, backup: bool) -> list[str]:
    """Apply parsed changes. Returns list of result messages."""
    results = []
    for ch in changes:
        fpath = os.path.join(root, ch["file"].lstrip("/\\"))
        mode  = ch["mode"]

        if mode == "replace_file":
            if backup and os.path.exists(fpath):
                _backup(fpath)
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(ch["to"])
            results.append(f"✔ replace_file  → {ch['file']}")

        elif mode == "replace_block":
            if not os.path.exists(fpath):
                results.append(f"✘ NOT FOUND     → {ch['file']}")
                continue
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            if ch["from"] not in content:
                results.append(f"✘ BLOCK MISSING → {ch['file']}")
                continue
            if backup:
                _backup(fpath)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content.replace(ch["from"], ch["to"], 1))
            results.append(f"✔ replace_block → {ch['file']}")

        elif mode == "insert_after":
            if not os.path.exists(fpath):
                results.append(f"✘ NOT FOUND     → {ch['file']}")
                continue
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            if ch["after"] not in content:
                results.append(f"✘ ANCHOR MISSING→ {ch['file']}")
                continue
            if backup:
                _backup(fpath)
            new = content.replace(ch["after"], ch["after"] + '\n' + ch["insert"], 1)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new)
            results.append(f"✔ insert_after  → {ch['file']}")

        elif mode == "delete_block":
            if not os.path.exists(fpath):
                results.append(f"✘ NOT FOUND     → {ch['file']}")
                continue
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            if ch["from"] not in content:
                results.append(f"✘ BLOCK MISSING → {ch['file']}")
                continue
            if backup:
                _backup(fpath)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content.replace(ch["from"], "", 1))
            results.append(f"✔ delete_block  → {ch['file']}")

    return results


def _backup(fpath: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = fpath + f".bak_{ts}"
    shutil.copy2(fpath, bak)


# ── RECENT POPUP ─────────────────────────────────────────────────────────────
class RecentPopup(QFrame):
    def __init__(self, parent, on_load, on_load_specific, on_remove):
        super().__init__(parent, Qt.WindowType.Popup)
        self.on_load          = on_load
        self.on_load_specific = on_load_specific
        self.on_remove        = on_remove
        self.setStyleSheet(f"""
            QFrame {{ background: #111111; border: 1px solid #00F0FF; }}
            QPushButton {{ background: transparent; border: none; color: #E0E0E0;
                           text-align: left; padding: 4px 8px; font-family: Consolas; font-size: 9pt; }}
            QPushButton:hover {{ background: #1e1e1e; color: #00F0FF; }}
            QPushButton#play {{ color: {CP_GREEN}; padding: 4px 6px; text-align: center; }}
            QPushButton#play:hover {{ background: {CP_GREEN}; color: #000; }}
            QPushButton#remove {{ color: #FF003C; padding: 4px 6px; text-align: center; }}
            QPushButton#remove:hover {{ background: #FF003C; color: #000; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        items = load_recent_details()
        if not items:
            lbl = QLabel("  No recent projects")
            lbl.setStyleSheet("color: #808080; padding: 8px; font-family: Consolas;")
            layout.addWidget(lbl)
            return
        for item in items:
            path = item["path"]
            files = item["files"]
            extensions = item.get("extensions", [])

            row = QWidget()
            row.setStyleSheet("background: transparent;")
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(0)

            btn_load = QPushButton(path)
            btn_load.setMinimumWidth(300)
            btn_load.clicked.connect(lambda _, p=path: (self.close(), self.on_load(p)))

            btn_play = QPushButton("▶")
            btn_play.setObjectName("play")
            btn_play.setFixedWidth(28)
            btn_play.setToolTip("Open only the files matching the extensions previously selected for this project")
            btn_play.clicked.connect(lambda _, p=path, f=files, e=extensions: (self.close(), self.on_load_specific(p, f, e)))

            btn_rem  = QPushButton("✕")
            btn_rem.setObjectName("remove")
            btn_rem.setFixedWidth(28)
            btn_rem.clicked.connect(lambda _, p=path: (self.close(), self.on_remove(p)))

            hl.addWidget(btn_load)
            hl.addWidget(btn_play)
            hl.addWidget(btn_rem)
            layout.addWidget(row)
        self.adjustSize()


# ── EXTENSION SELECTOR DIALOG ────────────────────────────────────────────────
SCRIPTS_EXTS = {'.py', '.ps1', '.bat', '.sh', '.cmd', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.cpp', '.c', '.h', '.cs', '.java', '.kt', '.rb', '.pl', '.php'}
WEB_EXTS     = {'.html', '.htm', '.css', '.scss', '.sass', '.less', '.vue', '.svelte'}

class ExtensionSelectorDialog(QDialog):
    def __init__(self, extensions: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("SELECT EXTENSIONS")
        self.setStyleSheet(THEME)

        self.checkboxes: dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        lbl = QLabel("Select file extensions to include:")
        lbl.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        layout.addWidget(lbl)

        # Using a QFrame instead of QScrollArea to prevent scrollbars and automatically fit content cleanly
        content_frame = QFrame()
        content_frame.setStyleSheet(f"QFrame {{ border: 1px solid {CP_DIM}; background-color: {CP_PANEL}; }}")
        vbox = QVBoxLayout(content_frame)
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(12)

        # Classify the found extensions
        scripts_found = []
        web_found     = []
        other_found   = []
        no_ext_found  = []

        for ext in sorted(extensions, key=lambda x: x.lower()):
            if ext == "":
                no_ext_found.append(ext)
                continue
            ext_lower = ext.lower()
            if ext_lower in SCRIPTS_EXTS:
                scripts_found.append(ext)
            elif ext_lower in WEB_EXTS:
                web_found.append(ext)
            else:
                other_found.append(ext)

        # 1st Row: Scripts
        if scripts_found:
            row1 = QHBoxLayout()
            row1.setSpacing(18)
            lbl_r1 = QLabel("SCRIPTS: ")
            lbl_r1.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold; min-width: 80px;")
            row1.addWidget(lbl_r1)
            for ext in scripts_found:
                chk = QCheckBox(ext)
                chk.setChecked(True)
                self.checkboxes[ext] = chk
                row1.addWidget(chk)
            row1.addStretch()
            vbox.addLayout(row1)

        # 2nd Row: Web related
        if web_found:
            row2 = QHBoxLayout()
            row2.setSpacing(18)
            lbl_r2 = QLabel("WEB:     ")
            lbl_r2.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; min-width: 80px;")
            row2.addWidget(lbl_r2)
            for ext in web_found:
                chk = QCheckBox(ext)
                chk.setChecked(True)
                self.checkboxes[ext] = chk
                row2.addWidget(chk)
            row2.addStretch()
            vbox.addLayout(row2)

        # 3rd Row: Data, Docs, Configuration, and Text Files
        if other_found:
            row3 = QHBoxLayout()
            row3.setSpacing(18)
            lbl_r3 = QLabel("DB & TXT:")
            lbl_r3.setStyleSheet(f"color: {CP_TEXT}; font-weight: bold; min-width: 80px;")
            row3.addWidget(lbl_r3)
            for ext in other_found:
                chk = QCheckBox(ext)
                chk.setChecked(True)
                self.checkboxes[ext] = chk
                row3.addWidget(chk)
            row3.addStretch()
            vbox.addLayout(row3)

        # 4th Row: Files with no extension
        if no_ext_found:
            row4 = QHBoxLayout()
            row4.setSpacing(18)
            lbl_r4 = QLabel("NO EXT:  ")
            lbl_r4.setStyleSheet(f"color: {CP_SUB}; font-weight: bold; min-width: 80px;")
            row4.addWidget(lbl_r4)
            for ext in no_ext_found:
                chk = QCheckBox("(no extension)")
                chk.setChecked(True)
                self.checkboxes[ext] = chk
                row4.addWidget(chk)
            row4.addStretch()
            vbox.addLayout(row4)

        layout.addWidget(content_frame)

        # ── Consolidated Button Row at the Bottom ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        # Selection Utilities (Left Aligned)
        btn_all = QPushButton("SELECT ALL")
        btn_none = QPushButton("SELECT NONE")
        btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_none.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_all.clicked.connect(self._select_all)
        btn_none.clicked.connect(self._select_none)
        btn_row.addWidget(btn_all)
        btn_row.addWidget(btn_none)

        btn_row.addStretch()

        # Action Confirmation (Right Aligned)
        btn_ok = QPushButton("✔ OK")
        btn_cancel = QPushButton("✕ CANCEL")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_ok.setStyleSheet(f"QPushButton {{ border-color: {CP_GREEN}; color: {CP_GREEN}; }}"
                             f"QPushButton:hover {{ background: {CP_GREEN}; color: #000; border-color: {CP_GREEN}; }}")
        btn_cancel.setStyleSheet(f"QPushButton {{ border-color: {CP_RED}; color: {CP_RED}; }}"
                                 f"QPushButton:hover {{ background: {CP_RED}; color: #000; border-color: {CP_RED}; }}")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        # Let Qt automatically scale the window to fit the contents perfectly
        self.adjustSize()

    def _select_all(self):
        for chk in self.checkboxes.values():
            chk.setChecked(True)

    def _select_none(self):
        for chk in self.checkboxes.values():
            chk.setChecked(False)

    def get_selected(self) -> set[str]:
        return {ext for ext, chk in self.checkboxes.items() if chk.isChecked()}


# ── IGNORE LIST DIALOG ───────────────────────────────────────────────────────
class IgnoreListDialog(QDialog):
    def __init__(self, current_custom: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("CUSTOM IGNORE EXTENSIONS")
        self.resize(460, 260)
        self.setStyleSheet(THEME)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        lbl = QLabel("Add extra extensions to ignore (comma-separated or on separate lines):")
        lbl.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        layout.addWidget(lbl)

        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("e.g.\n.mp3, .mp4\n.ogg, .wav")
        self.input_field.setPlainText(", ".join(sorted(current_custom)))
        layout.addWidget(self.input_field, 1)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("✔ SAVE")
        btn_cancel = QPushButton("✕ CANCEL")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_ok.setStyleSheet(f"QPushButton {{ border-color: {CP_GREEN}; color: {CP_GREEN}; }}"
                             f"QPushButton:hover {{ background: {CP_GREEN}; color: #000; border-color: {CP_GREEN}; }}")
        btn_cancel.setStyleSheet(f"QPushButton {{ border-color: {CP_RED}; color: {CP_RED}; }}"
                                 f"QPushButton:hover {{ background: {CP_RED}; color: #000; border-color: {CP_RED}; }}")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    def get_extensions(self) -> list[str]:
        raw = self.input_field.toPlainText()
        exts = []
        # Support splitting by both commas and newlines
        parts = raw.replace('\n', ',').split(',')
        for x in parts:
            cleaned = x.strip().lower()
            if cleaned:
                if not cleaned.startswith('.'):
                    cleaned = '.' + cleaned
                exts.append(cleaned)
        return exts


        btn_row_sel = QHBoxLayout()
        btn_all = QPushButton("SELECT ALL")
        btn_none = QPushButton("SELECT NONE")
        btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_none.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_all.clicked.connect(self._select_all)
        btn_none.clicked.connect(self._select_none)
        btn_row_sel.addWidget(btn_all)
        btn_row_sel.addWidget(btn_none)
        btn_row_sel.addStretch()
        layout.addLayout(btn_row_sel)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("✔ OK")
        btn_cancel = QPushButton("✕ CANCEL")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_ok.setStyleSheet(f"QPushButton {{ border-color: {CP_GREEN}; color: {CP_GREEN}; }}"
                             f"QPushButton:hover {{ background: {CP_GREEN}; color: #000; border-color: {CP_GREEN}; }}")
        btn_cancel.setStyleSheet(f"QPushButton {{ border-color: {CP_RED}; color: {CP_RED}; }}"
                                 f"QPushButton:hover {{ background: {CP_RED}; color: #000; border-color: {CP_RED}; }}")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    def _select_all(self):
        for chk in self.checkboxes.values():
            chk.setChecked(True)

    def _select_none(self):
        for chk in self.checkboxes.values():
            chk.setChecked(False)

    def get_selected(self) -> set[str]:
        return {ext for ext, chk in self.checkboxes.items() if chk.isChecked()}



# ── PREP TAB ──────────────────────────────────────────────────────────────────
class PrepTab(QWidget):
    def __init__(self, status_cb, root_cb=None):
        super().__init__()
        self.status_cb = status_cb
        self.root_cb = root_cb
        self.files: list[str] = []
        self.setAcceptDrops(True) # Enable Drag & Drop support for files and folders
        self._build()
        self._load_session()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        count_files = 0
        count_dirs = 0
        for url in urls:
            path = url.toLocalFile()
            if os.path.exists(path):
                if os.path.isdir(path):
                    self._load_dropped_dir(path)
                    count_dirs += 1
                elif os.path.isfile(path):
                    # Skip if the file extension is in the ignore list
                    if os.path.splitext(path)[1].lower() in IGNORE_EXTS:
                        continue
                    if path not in self.files:
                        self.files.append(path)
                        self._add_file_item(path)
                        count_files += 1

        if count_files > 0 or count_dirs > 0:
            self._update_root()
            self._save_session()
            self.status_cb(f"Dropped: {count_files} file(s) and {count_dirs} directory/directories processed")

    def _load_dropped_dir(self, d: str):
        # Scan for existing file extensions first, respecting ignore patterns
        found_exts = set()
        for root, dirs, fnames in os.walk(d):
            dirs[:] = [x for x in dirs if x not in IGNORE_PATTERNS and not x.startswith('.')]
            for fn in fnames:
                ext = os.path.splitext(fn)[1].lower()
                if ext in IGNORE_EXTS:
                    continue
                found_exts.add(ext)

        if not found_exts:
            return

        # Show selector dialog for toggling extensions
        dialog = ExtensionSelectorDialog(list(found_exts), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_exts = dialog.get_selected()
            self._load_dir(d, selected_exts, overwrite_recent=True)

    def _update_counter(self):
        text = self.prompt_out.toPlainText()
        char_count = len(text)
        # Using a solid /3.5 character ratio as a token proxy for code and natural text
        token_est = int(char_count / 3.5) if char_count > 0 else 0
        self.counter_lbl.setText(f"Size: {char_count:,} chars  |  ~{token_est:,} tokens")

    def _filter_files(self):
        query = self.search_input.text().strip().lower()
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            fp = item.data(Qt.ItemDataRole.UserRole)
            if not fp:
                continue
            # Show the item if search query matches file path or is empty
            match = (not query) or (query in fp.lower())
            item.setHidden(not match)



    def _save_session(self):
        import json
        try:
            with open(SESSION_PATH, 'r') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {}
        except Exception:
            data = {}
        data['files'] = self.files
        with open(SESSION_PATH, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_session(self):
        import json
        try:
            with open(SESSION_PATH, 'r') as f:
                data = json.load(f)
            saved = data if isinstance(data, list) else data.get('files', [])
            for fp in saved:
                if fp not in self.files and os.path.exists(fp):
                    self.files.append(fp)
                    self._add_file_item(fp)
            if self.files:
                self._update_root()
                self.status_cb(f"Restored {len(self.files)} file(s) from last session")
        except Exception:
            pass

    def _update_root(self):
        if self.root_cb and self.files:
            common = os.path.commonpath(self.files)
            if os.path.isfile(common):
                common = os.path.dirname(common)
            self.root_cb(common)

    def _add_file_item(self, fp: str):
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, fp) # Store the file path for fast filtering
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(widget)
        hl.setContentsMargins(4, 0, 4, 0)
        hl.setSpacing(4)

        lbl = QLabel(fp)
        
        # Smart file size analysis for warning highlights and context limits
        try:
            sz_bytes = os.path.getsize(fp)
            sz_kb = sz_bytes / 1024
            if sz_kb > 500:
                lbl_color = CP_RED
                lbl.setToolTip(f"⚠️ DANGER: Very large file ({sz_kb:.1f} KB).\nRecommended to exclude or split to prevent LLM context overflow.")
            elif sz_kb > 250:
                lbl_color = CP_YELLOW
                lbl.setToolTip(f"⚠️ WARNING: Large file ({sz_kb:.1f} KB).\nMay consume significant context window memory.")
            else:
                lbl_color = CP_TEXT
                lbl.setToolTip(f"File size: {sz_kb:.1f} KB")
        except Exception:
            lbl_color = CP_TEXT
            lbl.setToolTip("Could not read file size details")

        lbl.setStyleSheet(f"color: {lbl_color}; background: transparent; font-size: 9pt;")

        btn_rem = QPushButton("✕")
        btn_rem.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_rem.setFixedWidth(18)
        btn_rem.setFixedHeight(16)
        btn_rem.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: 1px solid {CP_DIM}; color: {CP_RED};
                padding: 0; font-family: 'Consolas'; font-size: 7pt; font-weight: bold;
            }}
            QPushButton:hover {{
                background: {CP_RED}; color: #000; border-color: {CP_RED};
            }}
        """)
        btn_rem.clicked.connect(lambda _, f=fp, it=item: self._remove_file(f, it))

        hl.addWidget(lbl, 1)
        hl.addWidget(btn_rem, 0)

        item.setSizeHint(QSize(100, 22))
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, widget)

    def _remove_file(self, fp: str, item: QListWidgetItem):
        if fp in self.files:
            self.files.remove(fp)
        row = self.file_list.row(item)
        if row >= 0:
            self.file_list.takeItem(row)
        self._update_root()
        self._save_session()
        self.status_cb(f"Removed: {os.path.basename(fp)}")

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── LEFT PANEL ───────────────────────────────────────────
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 6, 0)
        left_layout.setSpacing(8)

        grp_files = QGroupBox("SOURCE FILES")
        vf = QVBoxLayout(grp_files)

        # File List Search/Filter Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter files by name…")
        self.search_input.textChanged.connect(self._filter_files)
        vf.addWidget(self.search_input)

        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        vf.addWidget(self.file_list)
        left_layout.addWidget(grp_files, 1)

        btn_row = QHBoxLayout()
        btn_add     = QPushButton("＋ ADD FILES")
        btn_add_dir = QPushButton("📁 ADD DIR")
        btn_recent  = QPushButton("🕘 RECENT")
        btn_clear   = QPushButton("✕ CLEAR ALL")
        for b in (btn_add, btn_add_dir, btn_recent, btn_clear):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._add_files)
        btn_add_dir.clicked.connect(self._add_dir)
        btn_recent.clicked.connect(self._show_recent)
        btn_clear.clicked.connect(self._clear_files)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_add_dir)
        btn_row.addWidget(btn_recent)
        btn_row.addWidget(btn_clear)
        left_layout.addLayout(btn_row, 0)

        # ── RIGHT PANEL ──────────────────────────────────────────
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(6, 0, 0, 0)
        right_layout.setSpacing(8)

        # Task description
        grp_task = QGroupBox("TASK / INSTRUCTIONS  (optional)")
        vt = QVBoxLayout(grp_task)
        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("Describe what you want the AI to do…")
        self.task_input.setMaximumHeight(80)
        vt.addWidget(self.task_input)
        grp_task.setMaximumHeight(120)
        right_layout.addWidget(grp_task, 0)

        # Output prompt
        grp_out = QGroupBox("GENERATED PROMPT  (copy → paste into AI)")
        vo = QVBoxLayout(grp_out)
        self.prompt_out = QTextEdit()
        self.prompt_out.setReadOnly(True)
        self.prompt_out.setPlaceholderText("Click GENERATE to build prompt…")
        self.prompt_out.textChanged.connect(self._update_counter)
        vo.addWidget(self.prompt_out)

        # Live Token / Character Counter Label
        self.counter_lbl = QLabel("Size: 0 chars  |  ~0 tokens")
        self.counter_lbl.setStyleSheet(f"color: {CP_SUB}; font-size: 9pt; font-family: 'Consolas';")
        vo.addWidget(self.counter_lbl)

        right_layout.addWidget(grp_out, 1)

        # Buttons
        btn_row2 = QHBoxLayout()
        btn_gen  = QPushButton("⚡ GENERATE PROMPT")
        btn_copy = QPushButton("📋 COPY TO CLIPBOARD")
        btn_gen.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_gen.setStyleSheet(f"QPushButton {{ border-color: {CP_CYAN}; color: {CP_CYAN}; }}"
                              f"QPushButton:hover {{ background: {CP_CYAN}; color: #000; border-color: {CP_CYAN}; }}")
        btn_gen.clicked.connect(self._generate)
        btn_copy.clicked.connect(self._copy)
        btn_row2.addWidget(btn_gen)
        btn_row2.addWidget(btn_copy)
        right_layout.addLayout(btn_row2, 0)

        # Assemble Splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        layout.addWidget(splitter)

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self._add_file_item(f)
        self.status_cb(f"{len(self.files)} file(s) loaded")
        self._update_root()
        self._save_session()

    def _add_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not d:
            return

        # Scan for existing file extensions first, respecting ignore patterns
        found_exts = set()
        for root, dirs, fnames in os.walk(d):
            dirs[:] = [x for x in dirs if x not in IGNORE_PATTERNS and not x.startswith('.')]
            for fn in fnames:
                ext = os.path.splitext(fn)[1].lower()
                if ext in IGNORE_EXTS:
                    continue
                found_exts.add(ext)

        if not found_exts:
            self.status_cb("No valid files found in directory")
            return

        # Show selector dialog for toggling extensions
        dialog = ExtensionSelectorDialog(list(found_exts), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_exts = dialog.get_selected()
            self._load_dir(d, selected_exts, overwrite_recent=True)

    def _load_dir(self, d: str, selected_exts: set[str] = None, overwrite_recent: bool = False):
        count = 0
        added_files = []
        discovered_exts = set()
        for root, dirs, fnames in os.walk(d):
            # Skip ignored directories in-place
            dirs[:] = [x for x in dirs if x not in IGNORE_PATTERNS and not x.startswith('.')]
            for fn in fnames:
                ext = os.path.splitext(fn)[1].lower()
                if ext in IGNORE_EXTS:
                    continue
                discovered_exts.add(ext)
                if selected_exts is not None and ext not in selected_exts:
                    continue
                fp = os.path.join(root, fn)
                added_files.append(fp)
                if fp not in self.files:
                    self.files.append(fp)
                    self._add_file_item(fp)
                    count += 1
        
        exts_list = list(selected_exts) if selected_exts is not None else list(discovered_exts)
        add_recent(d, added_files, exts_list, overwrite_existing=overwrite_recent)
        self.status_cb(f"Added {count} file(s) from directory")
        self._update_root()
        self._save_session()

    def _load_specific_files(self, d: str, files: list[str], extensions: list[str]):
        if extensions:
            # Re-load the directory filtering specifically by the stored extensions
            self._load_dir(d, set(extensions), overwrite_recent=False)
        elif files:
            # Fallback to absolute file paths list if no extensions were registered
            count = 0
            for fp in files:
                if os.path.exists(fp) and fp not in self.files:
                    self.files.append(fp)
                    self._add_file_item(fp)
                    count += 1
            add_recent(d, files, [], overwrite_existing=False)
            self.status_cb(f"Restored {count} specific file(s) for project")
            self._update_root()
            self._save_session()
        else:
            self._load_dir(d, overwrite_recent=False)

    def _show_recent(self):
        btn = self.sender()
        popup = RecentPopup(
            self,
            on_load=self._load_dir,
            on_load_specific=self._load_specific_files,
            on_remove=lambda p: (
                remove_recent(p),
                self.status_cb(f"Removed: {p}")
            )
        )
        pos = btn.mapToGlobal(QPoint(0, btn.height()))
        popup.move(pos)
        popup.show()

    def _clear_files(self):
        self.files.clear()
        self.file_list.clear()
        self._save_session()
        self.status_cb("File list cleared")

    def _generate(self):
        if not self.files:
            self.status_cb("⚠ No files added")
            return

        guide = ""
        if os.path.exists(GUIDE_PATH):
            with open(GUIDE_PATH, 'r', encoding='utf-8') as f:
                guide = f.read()

        task = self.task_input.toPlainText().strip()
        parts = [guide]

        for fp in self.files:
            try:
                with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                ext = os.path.splitext(fp)[1].lstrip('.')
                parts.append(f"\n### `{fp}`\n```{ext}\n{content}\n```")
            except Exception as e:
                parts.append(f"\n### `{fp}`\n[ERROR reading file: {e}]")

        if task:
            parts.append(f"\n---\n## NOW DO THIS\n\n{task}")

        self.prompt_out.setPlainText('\n'.join(parts))
        self.status_cb("Prompt generated — copy and paste into AI")

    def _copy(self):
        text = self.prompt_out.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_cb("✔ Copied to clipboard")
        else:
            self.status_cb("⚠ Nothing to copy — generate first")


# ── MERGE TAB ─────────────────────────────────────────────────────────────────
class MergeTab(QWidget):
    def __init__(self, status_cb):
        super().__init__()
        self.status_cb = status_cb
        self._build()
        self._load_prefs()

    def _save_prefs(self):
        import json
        try:
            with open(SESSION_PATH, 'r') as f:
                data = json.load(f)
        except Exception:
            data = {}
        data['backup']  = self.chk_backup.isChecked()
        data['preview'] = self.chk_preview.isChecked()
        with open(SESSION_PATH, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_prefs(self):
        import json
        try:
            with open(SESSION_PATH, 'r') as f:
                data = json.load(f)
            if 'backup'  in data: self.chk_backup.setChecked(data['backup'])
            if 'preview' in data: self.chk_preview.setChecked(data['preview'])
        except Exception:
            pass

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Root dir
        grp_root = QGroupBox("PROJECT ROOT DIRECTORY")
        hr = QHBoxLayout(grp_root)
        self.root_input = QLineEdit()
        self.root_input.setPlaceholderText("Directory that contains your source files…")
        btn_browse = QPushButton("📁 BROWSE")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self._browse_root)
        hr.addWidget(self.root_input)
        hr.addWidget(btn_browse)
        layout.addWidget(grp_root)

        # AI response input
        grp_resp = QGroupBox("AI RESPONSE  (paste here — supports multiple partial blocks)")
        vr = QVBoxLayout(grp_resp)
        self.response_input = QTextEdit()
        self.response_input.setPlaceholderText("Paste the AI's response here…")
        vr.addWidget(self.response_input)
        layout.addWidget(grp_resp)

        # Options
        opt_row = QHBoxLayout()
        self.chk_backup = QCheckBox("Create .bak backups before modifying")
        self.chk_backup.setChecked(True)
        self.chk_preview = QCheckBox("Preview changes before applying")
        self.chk_preview.setChecked(True)
        self.chk_backup.toggled.connect(self._save_prefs)
        self.chk_preview.toggled.connect(self._save_prefs)
        opt_row.addWidget(self.chk_backup)
        opt_row.addWidget(self.chk_preview)
        opt_row.addStretch()
        layout.addLayout(opt_row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_parse  = QPushButton("🔍 PARSE CHANGES")
        btn_apply  = QPushButton("✔ APPLY CHANGES")
        btn_clear  = QPushButton("✕ CLEAR")
        btn_parse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_parse.setStyleSheet(f"QPushButton {{ border-color: {CP_CYAN}; color: {CP_CYAN}; }}"
                                f"QPushButton:hover {{ background: {CP_CYAN}; color: #000; border-color: {CP_CYAN}; }}")
        btn_apply.setStyleSheet(f"QPushButton {{ border-color: {CP_GREEN}; color: {CP_GREEN}; }}"
                                f"QPushButton:hover {{ background: {CP_GREEN}; color: #000; border-color: {CP_GREEN}; }}")
        btn_parse.clicked.connect(self._parse)
        btn_apply.clicked.connect(self._apply)
        btn_clear.clicked.connect(self._clear)
        btn_row.addWidget(btn_parse)
        btn_row.addWidget(btn_apply)
        btn_row.addWidget(btn_clear)
        layout.addLayout(btn_row)

        # Results
        grp_res = QGroupBox("RESULTS")
        vres = QVBoxLayout(grp_res)
        self.result_out = QTextEdit()
        self.result_out.setReadOnly(True)
        vres.addWidget(self.result_out)
        layout.addWidget(grp_res)

        self._pending_changes: list[dict] = []

    def _browse_root(self):
        d = QFileDialog.getExistingDirectory(self, "Select Project Root")
        if d:
            self.set_root(d)

    def set_root(self, path: str):
        self.root_input.setText(path)
        add_recent(path)

    

    def _parse(self):
        text = self.response_input.toPlainText().strip()
        if not text:
            self.status_cb("⚠ Paste AI response first")
            return
        self._pending_changes = parse_ai_response(text)
        if not self._pending_changes:
            self.result_out.setPlainText("⚠ No valid change blocks found.\nMake sure the AI followed the @@FILE / @@MODE / @@END format.")
            self.status_cb("No changes parsed")
            return

        lines = [f"Found {len(self._pending_changes)} change(s):\n"]
        for ch in self._pending_changes:
            lines.append(f"  [{ch['mode']:15s}] {ch['file']}")
        if self.chk_preview.isChecked():
            lines.append("\nReview above then click APPLY CHANGES.")
        self.result_out.setPlainText('\n'.join(lines))
        self.status_cb(f"Parsed {len(self._pending_changes)} change(s) — ready to apply")

    def _apply(self):
        if not self._pending_changes:
            self.status_cb("⚠ Parse changes first")
            return
        root = self.root_input.text().strip()
        if not root or not os.path.isdir(root):
            self.status_cb("⚠ Set a valid project root directory")
            return

        if self.chk_preview.isChecked():
            reply = QMessageBox.question(
                self, "CONFIRM APPLY",
                f"Apply {len(self._pending_changes)} change(s) to:\n{root}\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        results = apply_changes(self._pending_changes, root, self.chk_backup.isChecked())
        ok  = sum(1 for r in results if r.startswith("✔"))
        err = len(results) - ok
        self.result_out.setPlainText('\n'.join(results))
        self.status_cb(f"Done — {ok} applied, {err} failed")
        self._pending_changes = []

    def _clear(self):
        self.response_input.clear()
        self.result_out.clear()
        self._pending_changes = []
        self.status_cb("Cleared")


# ── MAIN WINDOW ───────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CODE MERGER  //  CYBERPUNK EDITION")
        self.resize(900, 680)
        self.setStyleSheet(THEME)
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 4)
        root_layout.setSpacing(6)

        # Header
        hdr = QLabel("// CODE MERGER")
        hdr.setStyleSheet(f"color: {CP_YELLOW}; font-size: 14pt; font-weight: bold; letter-spacing: 2px;")
        sub = QLabel("Prep files for AI  ·  Merge AI responses back to disk")
        sub.setStyleSheet(f"color: {CP_SUB}; font-size: 9pt;")
        root_layout.addWidget(hdr)
        root_layout.addWidget(sub)

        # Tabs
        self.tabs = QTabWidget()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._set_status("Ready")

        # Corner layout container for multiple buttons
        corner_widget = QWidget()
        corner_widget.setStyleSheet("background: transparent;")
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 2, 8, 2)
        corner_layout.setSpacing(6)

        btn_ignore = QPushButton("⚙ IGNORE LIST")
        btn_ignore.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ignore.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL};
                color: {CP_SUB};
                border: 1px solid {CP_DIM};
                padding: 4px 12px;
                font-family: 'Consolas';
                font-size: 9pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {CP_CYAN};
                border-color: {CP_CYAN};
                background-color: {CP_BG};
            }}
        """)
        btn_ignore.clicked.connect(self._manage_ignores)

        btn_restart = QPushButton("↺ RESTART")
        btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_restart.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL};
                color: {CP_SUB};
                border: 1px solid {CP_DIM};
                padding: 4px 12px;
                font-family: 'Consolas';
                font-size: 9pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {CP_YELLOW};
                border-color: {CP_YELLOW};
                background-color: {CP_BG};
            }}
            QPushButton:pressed {{
                color: {CP_CYAN};
            }}
        """)
        btn_restart.clicked.connect(lambda: os.execv(sys.executable, [sys.executable] + sys.argv))

        corner_layout.addWidget(btn_ignore)
        corner_layout.addWidget(btn_restart)
        self.tabs.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)

        self.merge_tab = MergeTab(self._set_status)
        self.prep_tab  = PrepTab(self._set_status, self.merge_tab.set_root)
        self.tabs.addTab(self.prep_tab,  "⚙  PREP  ( local → AI )")
        self.tabs.addTab(self.merge_tab, "⚡  MERGE  ( AI → local )")
        root_layout.addWidget(self.tabs)

    def _manage_ignores(self):
        dialog = IgnoreListDialog(list(CUSTOM_IGNORED_EXTS), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_exts = dialog.get_extensions()
            save_custom_ignores(new_exts)
            self._set_status(f"Updated ignore list with {len(new_exts)} custom extension(s)")

    def _set_status(self, msg: str):
        self.status_bar.showMessage(f"  {msg}")


if __name__ == "__main__":
    load_custom_ignores()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
