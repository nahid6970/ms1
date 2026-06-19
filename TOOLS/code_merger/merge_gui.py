import sys
import os
import re
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QGroupBox,
    QFileDialog, QListWidget, QListWidgetItem, QSplitter,
    QStatusBar, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
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
QListWidget::item:selected {{ background-color: {CP_CYAN}; color: #000; }}
QListWidget::item:hover {{ background-color: #1e1e1e; }}
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

GUIDE_PATH = os.path.join(os.path.dirname(__file__), "PROMPT_GUIDE.md")

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


# ── PREP TAB ──────────────────────────────────────────────────────────────────
class PrepTab(QWidget):
    def __init__(self, status_cb, root_cb=None):
        super().__init__()
        self.status_cb = status_cb
        self.root_cb = root_cb  # called with common root whenever files change
        self.files: list[str] = []
        self._build()

    def _update_root(self):
        if self.root_cb and self.files:
            common = os.path.commonpath(self.files)
            if os.path.isfile(common):
                common = os.path.dirname(common)
            self.root_cb(common)

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # File list group
        grp_files = QGroupBox("SOURCE FILES")
        vf = QVBoxLayout(grp_files)
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(120)
        btn_row = QHBoxLayout()
        btn_add  = QPushButton("＋ ADD FILES")
        btn_add_dir = QPushButton("📁 ADD DIR")
        btn_clear = QPushButton("✕ CLEAR")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_dir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._add_files)
        btn_add_dir.clicked.connect(self._add_dir)
        btn_clear.clicked.connect(self._clear_files)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_add_dir)
        btn_row.addWidget(btn_clear)
        vf.addWidget(self.file_list)
        vf.addLayout(btn_row)
        layout.addWidget(grp_files)

        # Task description
        grp_task = QGroupBox("TASK / INSTRUCTIONS  (optional)")
        vt = QVBoxLayout(grp_task)
        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("Describe what you want the AI to do…")
        self.task_input.setMaximumHeight(80)
        vt.addWidget(self.task_input)
        layout.addWidget(grp_task)

        # Output prompt
        grp_out = QGroupBox("GENERATED PROMPT  (copy → paste into AI)")
        vo = QVBoxLayout(grp_out)
        self.prompt_out = QTextEdit()
        self.prompt_out.setReadOnly(True)
        self.prompt_out.setPlaceholderText("Click GENERATE to build prompt…")
        vo.addWidget(self.prompt_out)
        layout.addWidget(grp_out)

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
        layout.addLayout(btn_row2)

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.file_list.addItem(QListWidgetItem(f))
        self.status_cb(f"{len(self.files)} file(s) loaded")
        self._update_root()

    def _add_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not d:
            return
        count = 0
        for root, _, fnames in os.walk(d):
            for fn in fnames:
                fp = os.path.join(root, fn)
                if fp not in self.files:
                    self.files.append(fp)
                    self.file_list.addItem(QListWidgetItem(fp))
                    count += 1
        self.status_cb(f"Added {count} file(s) from directory")
        self._update_root()

    def _clear_files(self):
        self.files.clear()
        self.file_list.clear()
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
        if task:
            parts.append(f"\n## MY REQUEST\n\n{task}\n")

        for fp in self.files:
            try:
                with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                ext = os.path.splitext(fp)[1].lstrip('.')
                parts.append(f"\n### `{fp}`\n```{ext}\n{content}\n```")
            except Exception as e:
                parts.append(f"\n### `{fp}`\n[ERROR reading file: {e}]")

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

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Root dir
        grp_root = QGroupBox("PROJECT ROOT DIRECTORY")
        hr = QHBoxLayout(grp_root)
        from PyQt6.QtWidgets import QLineEdit
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
        self.response_input.setPlaceholderText(
            "Paste the AI's response here.\n"
            "If the AI gave you multiple separate blocks/messages, use APPEND FROM CLIPBOARD "
            "to accumulate them all before parsing."
        )
        vr.addWidget(self.response_input)
        paste_row = QHBoxLayout()
        btn_paste_append = QPushButton("📋 APPEND FROM CLIPBOARD")
        btn_paste_append.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_paste_append.setToolTip("Appends clipboard content to whatever is already in the box")
        btn_paste_append.clicked.connect(self._append_clipboard)
        paste_row.addWidget(btn_paste_append)
        paste_row.addStretch()
        vr.addLayout(paste_row)
        layout.addWidget(grp_resp)

        # Options
        opt_row = QHBoxLayout()
        self.chk_backup = QCheckBox("Create .bak backups before modifying")
        self.chk_backup.setChecked(True)
        self.chk_preview = QCheckBox("Preview changes before applying")
        self.chk_preview.setChecked(True)
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
            self.root_input.setText(d)

    def set_root(self, path: str):
        self.root_input.setText(path)

    def _append_clipboard(self):
        clip = QApplication.clipboard().text()
        if not clip:
            self.status_cb("⚠ Clipboard is empty")
            return
        current = self.response_input.toPlainText()
        separator = "\n" if current and not current.endswith("\n") else ""
        self.response_input.setPlainText(current + separator + clip)
        self.status_cb("✔ Appended clipboard content")

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

        self.merge_tab = MergeTab(self._set_status)
        self.prep_tab  = PrepTab(self._set_status, self.merge_tab.set_root)
        self.tabs.addTab(self.prep_tab,  "⚙  PREP  ( local → AI )")
        self.tabs.addTab(self.merge_tab, "⚡  MERGE  ( AI → local )")
        root_layout.addWidget(self.tabs)

        # Footer buttons
        foot = QHBoxLayout()
        btn_restart = QPushButton("↺ RESTART")
        btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_restart.clicked.connect(lambda: os.execv(sys.executable, [sys.executable] + sys.argv))
        foot.addStretch()
        foot.addWidget(btn_restart)
        root_layout.addLayout(foot)

    def _set_status(self, msg: str):
        self.status_bar.showMessage(f"  {msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
