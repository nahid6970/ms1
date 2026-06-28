import sys
import os
import re
import shutil
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QGroupBox,
    QFileDialog, QListWidget, QListWidgetItem, QSplitter,
    QStatusBar, QCheckBox, QMessageBox, QLineEdit, QMenu, QFrame,
    QDialog, QScrollArea, QGridLayout, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QSpinBox
)
from PyQt6.QtCore import Qt, QPoint, QSize, QEvent, QByteArray
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap

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
MAX_RECENT   = 999999

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
EXTENSION_ICONS = {}
SOURCE_FILES_FONT_SIZE = 9
EXTENSION_ICON_SIZE = 16

try:
    from PyQt6.QtSvg import QSvgRenderer
    HAS_SVG = True
except ImportError:
    HAS_SVG = False

def render_extension_icon(icon_data: str, size: int = 16) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    icon_data = icon_data.strip()
    if not icon_data:
        return pixmap
        
    if icon_data.startswith("<") and "svg" in icon_data.lower():
        if HAS_SVG:
            try:
                renderer = QSvgRenderer(QByteArray(icon_data.encode('utf-8')))
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
            except Exception:
                pass
    else:
        painter = QPainter(pixmap)
        font = QFont()
        font.setPixelSize(size - 2)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, icon_data)
        painter.end()
        
    return pixmap

def load_settings():
    global CUSTOM_IGNORED_EXTS, EXTENSION_ICONS, SOURCE_FILES_FONT_SIZE, EXTENSION_ICON_SIZE
    try:
        if os.path.exists(SESSION_PATH):
            with open(SESSION_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                ignores = data.get('custom_ignored_exts', [])
                CUSTOM_IGNORED_EXTS = set(ignores)
                IGNORE_EXTS.update(CUSTOM_IGNORED_EXTS)
                
                EXTENSION_ICONS = data.get('extension_icons', {})
                SOURCE_FILES_FONT_SIZE = data.get('source_files_font_size', 9)
                EXTENSION_ICON_SIZE = data.get('extension_icon_size', 16)
    except Exception as e:
        print(f"Error loading settings: {e}", file=sys.stderr)

def save_settings(ignores: list[str], icons: dict[str, str], font_size: int, icon_size: int):
    global CUSTOM_IGNORED_EXTS, EXTENSION_ICONS, SOURCE_FILES_FONT_SIZE, EXTENSION_ICON_SIZE
    CUSTOM_IGNORED_EXTS = set(ignores)
    IGNORE_EXTS.update(CUSTOM_IGNORED_EXTS)
    EXTENSION_ICONS = icons
    SOURCE_FILES_FONT_SIZE = font_size
    EXTENSION_ICON_SIZE = icon_size
    try:
        data = {}
        if os.path.exists(SESSION_PATH):
            with open(SESSION_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {}
        data['custom_ignored_exts'] = list(CUSTOM_IGNORED_EXTS)
        data['extension_icons'] = EXTENSION_ICONS
        data['source_files_font_size'] = SOURCE_FILES_FONT_SIZE
        data['extension_icon_size'] = EXTENSION_ICON_SIZE
        with open(SESSION_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving settings: {e}", file=sys.stderr)


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
                name = item.get("name", "")
                files = item.get("files", [])
                extensions = item.get("extensions", [])
            else:
                p = item
                name = ""
                files = []
                extensions = []
            if not p:
                continue
            n = os.path.normpath(p)
            if n not in seen:
                seen.add(n)
                out_dict = {
                    "path": n, 
                    "files": files, 
                    "extensions": extensions,
                    "clicks": item.get("clicks", 0) if isinstance(item, dict) else 0
                }
                if name:
                    out_dict["name"] = name
                out.append(out_dict)
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

    name = existing.get("name", "") if existing else ""
    clicks = existing.get("clicks", 0) if existing else 0
    clicks += 1

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
    new_entry = {
        "path": path,
        "files": normalized_files,
        "extensions": extensions,
        "clicks": clicks
    }
    if name:
        new_entry["name"] = name
    current.insert(0, new_entry)
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


def analyze_match_failure(content: str, target_block: str, mode: str) -> str:
    """Analyze why target_block (either 'from' or 'after') was not found in content."""
    lines_content = content.splitlines()
    lines_block = target_block.splitlines()
    
    # Strip empty lines from block to find first meaningful line
    block_stripped = [l for l in lines_block if l.strip()]
    if not block_stripped:
        return "The block is empty."
    
    first_meaningful = block_stripped[0].strip()
    
    # Find matching lines in content
    matches = []
    for idx, line in enumerate(lines_content):
        if first_meaningful in line:
            matches.append(idx)
            
    if not matches:
        import difflib
        # Look for close matches of the first meaningful line in the file content
        close_matches = []
        for idx, line in enumerate(lines_content):
            ratio = difflib.SequenceMatcher(None, first_meaningful, line.strip()).ratio()
            if ratio >= 0.5:
                close_matches.append((idx + 1, line.strip(), ratio))
        
        # Sort by similarity ratio descending
        close_matches.sort(key=lambda x: x[2], reverse=True)
        
        analysis = (
            "The block's first meaningful line was not found in the file:\n"
            f"  Expected: \"{first_meaningful}\"\n"
        )
        if close_matches:
            analysis += "Here are the most similar lines found in the target file:\n"
            for line_num, line_text, ratio in close_matches[:3]:
                analysis += f"  - Line {line_num}: \"{line_text}\" (Similarity: {int(ratio*100)}%)\n"
        else:
            analysis += "No similar lines were found in the file. Check if this code belongs in this file or has been completely removed/renamed.\n"
        return analysis
    
    # Find the best match if there are multiple occurrences of the first line
    import difflib
    best_match_idx = matches[0]
    best_ratio = -1.0
    
    for start_idx in matches:
        actual_slice = lines_content[start_idx : start_idx + len(lines_block)]
        matcher = difflib.SequenceMatcher(None, actual_slice, lines_block)
        ratio = matcher.ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match_idx = start_idx
            
    actual_slice = lines_content[best_match_idx : best_match_idx + len(lines_block)]
    
    matched_lines = 0
    first_mismatch = None
    for i, expected in enumerate(lines_block):
        if i < len(actual_slice):
            actual = actual_slice[i]
            if expected == actual:
                matched_lines += 1
            elif first_mismatch is None:
                first_mismatch = (i, expected, actual)
        else:
            if first_mismatch is None:
                first_mismatch = (i, expected, None)

    summary = f"Out of {len(lines_block)} lines in the block, the first {matched_lines} lines matched perfectly.\n"
    if first_mismatch:
        idx, exp, act = first_mismatch
        summary += f"The divergence started at line {idx + 1} of the block (file line {best_match_idx + 1 + idx}):\n"
        summary += f"  Expected: {repr(exp)}\n"
        if act is not None:
            summary += f"  Actual:   {repr(act)}\n"
        else:
            summary += f"  Actual:   <End of file>\n"

    diff = difflib.unified_diff(
        actual_slice,
        lines_block,
        fromfile=f"Actual file content",
        tofile="Expected AI block",
        lineterm=""
    )
    diff_text = "\n".join(list(diff)[2:]) # Skip the --- and +++ lines
    
    return (
        f"The block's first line was found at line {best_match_idx + 1}.\n"
        f"{summary}\n"
        "Full diff of the expected block vs actual file:\n"
        f"{diff_text}"
    )


def apply_changes(changes: list[dict], root: str, backup: bool) -> list[str]:
    """Apply parsed changes. Returns list of result messages."""
    results = []
    for ch in changes:
        try:
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
                    results.append(
                        f"✘ NOT FOUND     → {ch['file']}\n"
                        f"  Mode: replace_block\n"
                        f"  File: {ch['file']}\n"
                        f"  Error: The target file does not exist at this path.\n"
                        f"  Root Directory: {root}\n"
                        f"  Attempted Full Path: {fpath}"
                    )
                    continue
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                if ch["from"] not in content:
                    try:
                        failure_info = analyze_match_failure(content, ch["from"], "replace_block")
                    except Exception as ex:
                        failure_info = f"Failed to generate diff analysis: {str(ex)}"
                    results.append(
                        f"✘ BLOCK MISSING → {ch['file']}\n"
                        f"  Mode: replace_block\n"
                        f"  File: {ch['file']}\n"
                        f"  Error: Block to replace was not found in the file.\n"
                        f"  Analysis:\n  {failure_info.replace('\n', '\n  ')}"
                    )
                    continue
                if backup:
                    _backup(fpath)
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content.replace(ch["from"], ch["to"], 1))
                results.append(f"✔ replace_block → {ch['file']}")

            elif mode == "insert_after":
                if not os.path.exists(fpath):
                    results.append(
                        f"✘ NOT FOUND     → {ch['file']}\n"
                        f"  Mode: insert_after\n"
                        f"  File: {ch['file']}\n"
                        f"  Error: The target file does not exist at this path.\n"
                        f"  Root Directory: {root}\n"
                        f"  Attempted Full Path: {fpath}"
                    )
                    continue
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                if ch["after"] not in content:
                    try:
                        failure_info = analyze_match_failure(content, ch["after"], "insert_after")
                    except Exception as ex:
                        failure_info = f"Failed to generate diff analysis: {str(ex)}"
                    results.append(
                        f"✘ ANCHOR MISSING→ {ch['file']}\n"
                        f"  Mode: insert_after\n"
                        f"  File: {ch['file']}\n"
                        f"  Error: Anchor block to insert after was not found in the file.\n"
                        f"  Analysis:\n  {failure_info.replace('\n', '\n  ')}"
                    )
                    continue
                if backup:
                    _backup(fpath)
                new = content.replace(ch["after"], ch["after"] + '\n' + ch["insert"], 1)
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new)
                results.append(f"✔ insert_after  → {ch['file']}")

            elif mode == "delete_block":
                if not os.path.exists(fpath):
                    results.append(
                        f"✘ NOT FOUND     → {ch['file']}\n"
                        f"  Mode: delete_block\n"
                        f"  File: {ch['file']}\n"
                        f"  Error: The target file does not exist at this path.\n"
                        f"  Root Directory: {root}\n"
                        f"  Attempted Full Path: {fpath}"
                    )
                    continue
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                if ch["from"] not in content:
                    try:
                        failure_info = analyze_match_failure(content, ch["from"], "delete_block")
                    except Exception as ex:
                        failure_info = f"Failed to generate diff analysis: {str(ex)}"
                    results.append(
                        f"✘ BLOCK MISSING → {ch['file']}\n"
                        f"  Mode: delete_block\n"
                        f"  File: {ch['file']}\n"
                        f"  Error: Block to delete was not found in the file.\n"
                        f"  Analysis:\n  {failure_info.replace('\n', '\n  ')}"
                    )
                    continue
                if backup:
                    _backup(fpath)
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content.replace(ch["from"], "", 1))
                results.append(f"✔ delete_block  → {ch['file']}")

        except Exception as outer_ex:
            results.append(
                f"✘ CRITICAL ERROR→ {ch.get('file', 'unknown')}\n"
                f"  Mode: {ch.get('mode', 'unknown')}\n"
                f"  File: {ch.get('file', 'unknown')}\n"
                f"  Error: An unexpected exception occurred while applying changes ({str(outer_ex)})."
            )

    return results


def _backup(fpath: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = fpath + f".bak_{ts}"
    shutil.copy2(fpath, bak)


# ── TOKEN OPTIMIZATION LOGIC ──────────────────────────────────────────────────

def minify_code(content: str, ext: str) -> str:
    """Minify code by stripping comments and redundant blank lines based on file extension."""
    ext = ext.lower()
    
    if ext == '.py':
        try:
            import ast
            tree = ast.parse(content)
            # Remove docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                    if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                        node.body.pop(0)
                        if not node.body:
                            node.body.append(ast.Pass())
            return ast.unparse(tree)
        except Exception:
            # Fallback if parsing fails
            pass

    if ext in ('.js', '.ts', '.tsx', '.jsx', '.cs', '.java', '.cpp', '.h', '.go', '.rs', '.swift', '.css', '.scss'):
        # Strip block comments /* ... */
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Strip line comments // ... (basic regex)
        lines = []
        for line in content.splitlines():
            stripped_line = re.sub(r'(?<!:)\/\/.*$', '', line)
            if stripped_line.strip() or line.strip() == '':
                lines.append(stripped_line)
        content = '\n'.join(lines)
        
    elif ext == '.ps1':
        # Strip block comments <# ... #>
        content = re.sub(r'<#.*?#>', '', content, flags=re.DOTALL)
        # Strip line comments # ...
        lines = []
        for line in content.splitlines():
            stripped_line = re.sub(r'#.*$', '', line)
            if stripped_line.strip() or line.strip() == '':
                lines.append(stripped_line)
        content = '\n'.join(lines)
        
    # Remove redundant consecutive blank lines
    lines = []
    prev_empty = False
    for line in content.splitlines():
        is_empty = not line.strip()
        if is_empty:
            if not prev_empty:
                lines.append('')
                prev_empty = True
        else:
            lines.append(line)
            prev_empty = False
            
    # Remove leading/trailing blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
        
    return '\n'.join(lines)


def fallback_skeletonize_py(content: str) -> str:
    lines = content.splitlines()
    out = []
    in_def = False
    def_indent = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())
        
        if in_def:
            if indent <= def_indent and stripped:
                in_def = False
            else:
                continue
        
        if stripped.startswith(("def ", "async def ")):
            out.append(line)
            out.append(" " * (indent + 4) + "pass")
            in_def = True
            def_indent = indent
        elif stripped.startswith("class "):
            out.append(line)
        elif indent == 0:
            out.append(line)
    return "\n".join(out)


def skeletonize_js_ts(content: str) -> str:
    lines = content.splitlines()
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        is_decl = False
        if stripped.startswith((
            "class ", "export class ", "interface ", "export interface ",
            "type ", "export type ", "function ", "export function ", "async function ", "export async function ",
            "const ", "export const ", "let ", "export let ", "var ", "export var "
        )):
            is_decl = True
        elif "(" in stripped and ")" in stripped and stripped.rstrip().endswith("{"):
            is_decl = True
            
        if is_decl:
            if "(" in stripped:
                decl = line.split("{")[0].rstrip()
                indent = len(line) - len(line.lstrip())
                out.append(" " * indent + decl + " { /* ... */ }")
            else:
                out.append(line)
        elif stripped.startswith("import ") or stripped.startswith("require("):
            out.append(line)
            
    return "\n".join(out)


def skeletonize_powershell(content: str) -> str:
    lines = content.splitlines()
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("function ") or stripped.startswith("filter "):
            decl = line.split("{")[0].rstrip()
            indent = len(line) - len(line.lstrip())
            out.append(" " * indent + decl + " { <# ... #> }")
        elif stripped.startswith("[CmdletBinding") or stripped.startswith("param("):
            out.append(line)
        elif stripped.startswith("#"):
            if any(tag in stripped.lower() for tag in [".synopsis", ".description", ".parameter"]):
                out.append(line)
    return "\n".join(out)


def skeletonize_code(content: str, ext: str) -> str:
    """Skeletonize code: return only API outline and strip function bodies."""
    ext = ext.lower()
    
    if ext == '.py':
        try:
            import ast
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        node.body = [ast.Expr(value=ast.Constant(value=docstring)), ast.Pass()]
                    else:
                        node.body = [ast.Pass()]
            return ast.unparse(tree)
        except Exception:
            return fallback_skeletonize_py(content)
            
    elif ext in ('.js', '.ts', '.tsx', '.jsx'):
        return skeletonize_js_ts(content)
        
    elif ext == '.ps1':
        return skeletonize_powershell(content)
        
    else:
        lines = content.splitlines()
        if len(lines) > 50:
            return '\n'.join(lines[:50]) + f"\n\n{get_comment_char(ext)} ... [TRUNCATED REFERENCE FILE] ..."
        return content


def get_comment_char(ext: str) -> str:
    ext = ext.lower()
    if ext in ('.py', '.ps1', '.sh', '.yaml', '.yml', '.ini', '.properties'):
        return "#"
    elif ext in ('.html', '.xml', '.vue', '.svg'):
        return "<!--"
    return "//"


# ── RECENT POPUP ─────────────────────────────────────────────────────────────
class RecentPopup(QFrame):
    def __init__(self, parent, on_load, on_load_all, on_remove, on_rename=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.on_load     = on_load
        self.on_load_all  = on_load_all
        self.on_remove    = on_remove
        self.on_rename    = on_rename
        self.sort_mode   = "Rec"
        try:
            if os.path.exists(SESSION_PATH):
                import json
                with open(SESSION_PATH, 'r') as f:
                    data = json.load(f)
                if isinstance(data, dict) and 'recent_sort_mode' in data:
                    self.sort_mode = data['recent_sort_mode']
        except Exception:
            pass
        self.setStyleSheet(f"""
            QFrame {{ background: #111111; border: 1px solid #00F0FF; }}
            QPushButton {{ background: transparent; border: none; color: #E0E0E0;
                           text-align: left; padding: 4px 8px; font-family: Consolas; font-size: 9pt; }}
            QPushButton:hover {{ background: #1e1e1e; color: #00F0FF; }}
            QPushButton#load_all {{ color: {CP_GREEN}; padding: 4px 6px; text-align: center; }}
            QPushButton#load_all:hover {{ background: {CP_GREEN}; color: #000; }}
            QPushButton#open {{ color: {CP_YELLOW}; padding: 4px 6px; text-align: center; }}
            QPushButton#open:hover {{ background: {CP_YELLOW}; color: #000; }}
            QPushButton#rename {{ color: {CP_CYAN}; padding: 4px 6px; text-align: center; }}
            QPushButton#rename:hover {{ background: {CP_CYAN}; color: #000; }}
            QPushButton#remove {{ color: #FF003C; padding: 4px 6px; text-align: center; }}
            QPushButton#remove:hover {{ background: #FF003C; color: #000; }}
            QScrollArea {{ border: none; background: transparent; }}
        """)
        self._build()

    def _build(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        items = load_recent_details()
        if not items:
            lbl = QLabel("  No recent projects")
            lbl.setStyleSheet("color: #808080; padding: 8px; font-family: Consolas;")
            main_layout.addWidget(lbl)
            self.adjustSize()
            return

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(content)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)

        self.project_rows = []

        for idx, item in enumerate(items):
            path = item["path"]
            name = item.get("name")
            files = item.get("files", [])
            extensions = item.get("extensions", [])
            clicks = item.get("clicks", 0)

            row = QWidget()
            row.setStyleSheet("background: transparent;")
            hl = QHBoxLayout(row)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(0)

            display_text = name if name else path
            btn_load = QPushButton(display_text)
            btn_load.setMinimumWidth(320)
            if name:
                btn_load.setToolTip(f"{path}\n\nLoad only the {len(files)} saved file(s) for this project (Opened: {clicks} time(s))")
            else:
                btn_load.setToolTip(f"Load only the {len(files)} saved file(s) for this project (Opened: {clicks} time(s))")
            btn_load.clicked.connect(lambda _, p=path, f=files, e=extensions: (self.close(), self.on_load(p, f, e)))

            btn_rename = QPushButton("I")
            btn_rename.setObjectName("rename")
            btn_rename.setFixedWidth(28)
            btn_rename.setToolTip("Rename this project alias")
            if self.on_rename:
                btn_rename.clicked.connect(lambda _, p=path: (self.close(), self.on_rename(p)))

            btn_open = QPushButton("📂")
            btn_open.setObjectName("open")
            btn_open.setFixedWidth(28)
            btn_open.setToolTip("Open project folder in File Explorer")
            btn_open.clicked.connect(lambda _, p=path: (self.close(), self._open_explorer(p)))

            btn_load_all = QPushButton("🔄")
            btn_load_all.setObjectName("load_all")
            btn_load_all.setFixedWidth(28)
            btn_load_all.setToolTip("Re-scan directory and load ALL non-ignored files, updating project in JSON")
            btn_load_all.clicked.connect(lambda _, p=path: (self.close(), self.on_load_all(p)))

            btn_rem  = QPushButton("✕  ")
            btn_rem.setObjectName("remove")
            btn_rem.setFixedWidth(50)
            btn_rem.clicked.connect(lambda _, p=path: (self.close(), self.on_remove(p)))

            hl.addWidget(btn_load)
            hl.addWidget(btn_rename)
            hl.addWidget(btn_open)
            hl.addWidget(btn_load_all)
            hl.addWidget(btn_rem)
            self.list_layout.addWidget(row)

            self.project_rows.append({
                "widget": row,
                "display_text": display_text,
                "path": path,
                "order_index": idx,
                "clicks": clicks
            })

        scroll.setWidget(content)
        scroll.setMaximumHeight(240)
        main_layout.addWidget(scroll)

        # Search box widget at the bottom
        search_widget = QWidget()
        search_widget.setStyleSheet(f"background-color: {CP_PANEL}; border-top: 1px solid {CP_DIM};")
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(6, 6, 6, 6)
        search_layout.setSpacing(4)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search recent projects…")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CP_BG};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 4px 8px;
                font-family: 'Consolas';
                font-size: 9pt;
            }}
            QLineEdit:focus {{
                border: 1px solid {CP_CYAN};
            }}
        """)
        self.search_input.textChanged.connect(self._filter_items)
        search_layout.addWidget(self.search_input, 1)

        self.btn_sort = QPushButton()
        self.btn_sort.setFixedWidth(90)
        self.btn_sort.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sort.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_BG};
                color: {CP_YELLOW};
                border: 1px solid {CP_DIM};
                font-family: 'Consolas';
                font-size: 8pt;
                font-weight: bold;
                padding: 4px;
            }}
            QPushButton:hover {{
                border-color: {CP_YELLOW};
                color: white;
                background-color: #222;
            }}
        """)
        if self.sort_mode == "Rec":
            self.btn_sort.setText("SORT: REC")
        elif self.sort_mode == "Name":
            self.btn_sort.setText("SORT: A-Z")
        elif self.sort_mode == "Path":
            self.btn_sort.setText("SORT: DIR")
        elif self.sort_mode == "Clicks":
            self.btn_sort.setText("SORT: CLK")

        self.btn_sort.clicked.connect(self._toggle_sort)
        search_layout.addWidget(self.btn_sort, 0)

        main_layout.addWidget(search_widget)

        self.adjustSize()
        self.search_input.setFocus()

        self._apply_sort()

    def _toggle_sort(self):
        if self.sort_mode == "Rec":
            self.sort_mode = "Name"
            self.btn_sort.setText("SORT: A-Z")
        elif self.sort_mode == "Name":
            self.sort_mode = "Path"
            self.btn_sort.setText("SORT: DIR")
        elif self.sort_mode == "Path":
            self.sort_mode = "Clicks"
            self.btn_sort.setText("SORT: CLK")
        else:
            self.sort_mode = "Rec"
            self.btn_sort.setText("SORT: REC")

        try:
            import json
            data = {}
            if os.path.exists(SESSION_PATH):
                with open(SESSION_PATH, 'r') as f:
                    data = json.load(f)
            if not isinstance(data, dict):
                data = {}
            data['recent_sort_mode'] = self.sort_mode
            with open(SESSION_PATH, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
            
        self._apply_sort()

    def _apply_sort(self):
        if self.sort_mode == "Rec":
            self.project_rows.sort(key=lambda x: x["order_index"])
        elif self.sort_mode == "Name":
            self.project_rows.sort(key=lambda x: x["display_text"].lower())
        elif self.sort_mode == "Path":
            self.project_rows.sort(key=lambda x: x["path"].lower())
        elif self.sort_mode == "Clicks":
            self.project_rows.sort(key=lambda x: x["clicks"], reverse=True)

        while self.list_layout.count() > 0:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        for item_data in self.project_rows:
            self.list_layout.addWidget(item_data["widget"])

        self.list_layout.addStretch()
        self._filter_items()

    def _filter_items(self):
        query = self.search_input.text().strip().lower()
        for item_data in self.project_rows:
            row = item_data["widget"]
            display_text = item_data["display_text"].lower()
            path = item_data["path"].lower()
            visible = (not query) or (query in display_text) or (query in path)
            row.setVisible(visible)

    def _open_explorer(self, p):
        try:
            if hasattr(os, 'startfile'):
                os.startfile(p)
            else:
                import subprocess
                subprocess.Popen(['explorer', p])
        except Exception:
            pass


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


# ── SETTINGS DIALOG ──────────────────────────────────────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SETTINGS")
        self.resize(550, 480)
        self.setStyleSheet(THEME)

        self.custom_ignores = list(CUSTOM_IGNORED_EXTS)
        self.icons = dict(EXTENSION_ICONS)
        self.font_size = SOURCE_FILES_FONT_SIZE
        self.icon_size = EXTENSION_ICON_SIZE

        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.tabs = QTabWidget()

        # --- TAB 1: IGNORE LIST ---
        tab_ignore = QWidget()
        v_ignore = QVBoxLayout(tab_ignore)
        v_ignore.setContentsMargins(8, 8, 8, 8)
        v_ignore.setSpacing(8)

        lbl_ignore = QLabel("Add extra extensions to ignore (comma-separated or on separate lines):")
        lbl_ignore.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        v_ignore.addWidget(lbl_ignore)

        self.ignore_input = QTextEdit()
        self.ignore_input.setPlaceholderText("e.g.\n.mp3, .mp4\n.ogg, .wav")
        self.ignore_input.setPlainText(", ".join(sorted(self.custom_ignores)))
        v_ignore.addWidget(self.ignore_input)

        self.tabs.addTab(tab_ignore, "🚫 IGNORE LIST")

        # --- TAB 2: EXTENSION ICONS ---
        tab_icons = QWidget()
        v_icons = QVBoxLayout(tab_icons)
        v_icons.setContentsMargins(8, 8, 8, 8)
        v_icons.setSpacing(8)

        lbl_icons = QLabel("Map file extensions to SVG icons / Nerd Font / Emojis:")
        lbl_icons.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        v_icons.addWidget(lbl_icons)

        # Quick Add Form (With 2 fields: Extension name and Icon input field)
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 4)
        form_layout.setSpacing(6)

        self.input_ext = QLineEdit()
        self.input_ext.setPlaceholderText(".ext (e.g., .py)")
        self.input_ext.setStyleSheet(f"background-color: {CP_BG}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;")

        self.input_icon = QLineEdit()
        self.input_icon.setPlaceholderText("Emoji, Nerd Font, or SVG XML...")
        self.input_icon.setStyleSheet(f"background-color: {CP_BG}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;")

        btn_form_add = QPushButton("＋ ADD")
        btn_form_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_form_add.clicked.connect(self._add_from_form)
        btn_form_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white;
                padding: 4px 12px; font-weight: bold; font-family: 'Consolas'; font-size: 9pt;
            }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
        """)

        form_layout.addWidget(QLabel("Ext:"), 0)
        form_layout.addWidget(self.input_ext, 1)
        form_layout.addWidget(QLabel("Icon:"), 0)
        form_layout.addWidget(self.input_icon, 2)
        form_layout.addWidget(btn_form_add, 0)

        v_icons.addWidget(form_widget)

        # Table of icons
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Extension", "Icon Value"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 120)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {CP_PANEL};
                gridline-color: {CP_DIM};
                border: 1px solid {CP_DIM};
                color: {CP_TEXT};
                font-family: 'Consolas';
                font-size: 9pt;
            }}
            QHeaderView::section {{
                background-color: {CP_PANEL};
                color: {CP_YELLOW};
                border: 1px solid {CP_DIM};
                padding: 4px;
                font-family: 'Consolas';
                font-size: 9pt;
            }}
            QTableWidget::item:selected {{
                background-color: #1a3a3a;
                color: {CP_CYAN};
            }}
        """)
        v_icons.addWidget(self.table)

        # Row with Add / Delete buttons
        h_btn = QHBoxLayout()
        btn_add = QPushButton("＋ ADD BLANK ROW")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._add_row)

        btn_delete = QPushButton("✕ DELETE SELECTED")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.clicked.connect(self._delete_row)

        h_btn.addWidget(btn_add)
        h_btn.addWidget(btn_delete)
        v_icons.addLayout(h_btn)

        self.tabs.addTab(tab_icons, "🎨 EXTENSION ICONS")

        # Populate table
        for ext, icon_val in sorted(self.icons.items()):
            self._insert_table_row(ext, icon_val)

        # --- TAB 3: DISPLAY SIZES ---
        tab_font = QWidget()
        v_font = QVBoxLayout(tab_font)
        v_font.setContentsMargins(8, 8, 8, 8)
        v_font.setSpacing(12)

        lbl_font = QLabel("Adjust display settings:")
        lbl_font.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        v_font.addWidget(lbl_font)

        # Source Files List Font Size
        h_font_settings = QHBoxLayout()
        lbl_fs = QLabel("Source Files List Font Size (pt):")
        lbl_fs.setStyleSheet(f"color: {CP_TEXT};")

        self.spin_fs = QSpinBox()
        self.spin_fs.setRange(6, 24)
        self.spin_fs.setValue(self.font_size)
        self.spin_fs.setStyleSheet(f"""
            QSpinBox {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 4px;
            }}
        """)
        h_font_settings.addWidget(lbl_fs)
        h_font_settings.addWidget(self.spin_fs)
        h_font_settings.addStretch()

        v_font.addLayout(h_font_settings)

        # Extension Icon Display Size
        h_icon_settings = QHBoxLayout()
        lbl_is = QLabel("Extension Icon Display Size (px):")
        lbl_is.setStyleSheet(f"color: {CP_TEXT};")

        self.spin_is = QSpinBox()
        self.spin_is.setRange(8, 48)
        self.spin_is.setValue(self.icon_size)
        self.spin_is.setStyleSheet(f"""
            QSpinBox {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 4px;
            }}
        """)
        h_icon_settings.addWidget(lbl_is)
        h_icon_settings.addWidget(self.spin_is)
        h_icon_settings.addStretch()

        v_font.addLayout(h_icon_settings)
        v_font.addStretch()

        self.tabs.addTab(tab_font, "🅰 DISPLAY SIZES")

        layout.addWidget(self.tabs)

        # Bottom save/cancel buttons
        btn_row = QHBoxLayout()
        btn_ok = QPushButton("✔ SAVE")
        btn_cancel = QPushButton("✕ CANCEL")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_ok.setStyleSheet(f"QPushButton {{ border-color: {CP_GREEN}; color: {CP_GREEN}; }}"
                             f"QPushButton:hover {{ background: {CP_GREEN}; color: #000; border-color: {CP_GREEN}; }}")
        btn_cancel.setStyleSheet(f"QPushButton {{ border-color: {CP_RED}; color: {CP_RED}; }}"
                                 f"QPushButton:hover {{ background: {CP_RED}; color: #000; border-color: {CP_RED}; }}")

        btn_ok.clicked.connect(self._on_save)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white;
                padding: 4px 10px; font-weight: bold; font-family: 'Consolas'; font-size: 9pt;
            }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
        """)
        btn_delete.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_RED}; color: {CP_RED};
                padding: 4px 10px; font-weight: bold; font-family: 'Consolas'; font-size: 9pt;
            }}
            QPushButton:hover {{ background-color: {CP_RED}; color: black; }}
        """)

    def _add_from_form(self):
        ext = self.input_ext.text().strip()
        icon = self.input_icon.text().strip()
        if not ext:
            return
        if not ext.startswith('.'):
            ext = '.' + ext
        if not icon:
            return
        
        # Check if already exists in table, if so update it
        exists = False
        for r in range(self.table.rowCount()):
            ext_item = self.table.item(r, 0)
            if ext_item and ext_item.text().strip().lower() == ext.lower():
                cell_widget = self.table.cellWidget(r, 1)
                if cell_widget:
                    val_input = cell_widget.findChild(QLineEdit)
                    if val_input:
                        val_input.setText(icon)
                exists = True
                break
        
        if not exists:
            self._insert_table_row(ext, icon)
            
        self.input_ext.clear()
        self.input_icon.clear()

    def _insert_table_row(self, ext: str = "", icon_value: str = ""):
        row = self.table.rowCount()
        self.table.insertRow(row)

        ext_item = QTableWidgetItem(ext)
        ext_item.setFont(QFont("Consolas", 10))
        self.table.setItem(row, 0, ext_item)

        widget = QWidget()
        hl = QHBoxLayout(widget)
        hl.setContentsMargins(2, 2, 2, 2)
        hl.setSpacing(4)

        val_input = QLineEdit(icon_value)
        val_input.setStyleSheet(f"background-color: {CP_BG}; color: {CP_CYAN}; border: 1px solid {CP_DIM};")
        val_input.setFont(QFont("Consolas", 9))
        val_input.setToolTip("Enter an Emoji, Nerd Font character, or raw SVG XML code.")

        btn_edit = QPushButton("✏️")
        btn_edit.setFixedWidth(28)
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet(f"QPushButton {{ background-color: {CP_DIM}; padding: 2px; }}")
        btn_edit.clicked.connect(lambda _, inp=val_input: self._open_multiline_editor(inp))

        hl.addWidget(val_input, 1)
        hl.addWidget(btn_edit, 0)

        self.table.setCellWidget(row, 1, widget)

    def _open_multiline_editor(self, line_edit: QLineEdit):
        dialog = QDialog(self)
        dialog.setWindowTitle("EDIT ICON VALUE")
        dialog.resize(400, 300)
        dialog.setStyleSheet(THEME)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        lbl = QLabel("Paste raw SVG XML code, Emoji, or Nerd Font character:")
        lbl.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        layout.addWidget(lbl)

        txt = QTextEdit()
        txt.setPlainText(line_edit.text())
        txt.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM};")
        txt.setFont(QFont("Consolas", 10))
        layout.addWidget(txt)

        btn_row = QHBoxLayout()
        btn_ok = QPushButton("✔ APPLY")
        btn_cancel = QPushButton("✕ CANCEL")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_ok.setStyleSheet(f"QPushButton {{ border-color: {CP_GREEN}; color: {CP_GREEN}; }}"
                             f"QPushButton:hover {{ background: {CP_GREEN}; color: #000; border-color: {CP_GREEN}; }}")
        btn_cancel.setStyleSheet(f"QPushButton {{ border-color: {CP_RED}; color: {CP_RED}; }}"
                                 f"QPushButton:hover {{ background: {CP_RED}; color: #000; border-color: {CP_RED}; }}")

        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)

        btn_row.addStretch()
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            line_edit.setText(txt.toPlainText().strip())

    def _add_row(self):
        self._insert_table_row("", "")

    def _delete_row(self):
        curr_row = self.table.currentRow()
        if curr_row >= 0:
            self.table.removeRow(curr_row)

    def _get_icon_mappings(self) -> dict[str, str]:
        mappings = {}
        for row in range(self.table.rowCount()):
            ext_item = self.table.item(row, 0)
            ext = ext_item.text().strip().lower() if ext_item else ""
            if not ext:
                continue
            if not ext.startswith('.'):
                ext = '.' + ext

            cell_widget = self.table.cellWidget(row, 1)
            if cell_widget:
                path_input = cell_widget.findChild(QLineEdit)
                path = path_input.text().strip() if path_input else ""
                if path:
                    mappings[ext] = path
        return mappings

    def _on_save(self):
        raw_ignores = self.ignore_input.toPlainText()
        ignores = []
        parts = raw_ignores.replace('\n', ',').split(',')
        for x in parts:
            cleaned = x.strip().lower()
            if cleaned:
                if not cleaned.startswith('.'):
                    cleaned = '.' + cleaned
                ignores.append(cleaned)

        icons = self._get_icon_mappings()
        font_size = self.spin_fs.value()
        icon_size = self.spin_is.value()

        save_settings(ignores, icons, font_size, icon_size)
        self.accept()


# ── PREP TAB ──────────────────────────────────────────────────────────────────
class PrepTab(QWidget):
    def __init__(self, status_cb, root_cb=None):
        super().__init__()
        self.status_cb = status_cb
        self.root_cb = root_cb
        self.files: list[str] = []
        self.file_modes: dict[str, str] = {}
        self.project_root = ""
        self.setAcceptDrops(True) # Enable Drag & Drop support for files and folders
        self._build()
        self._load_session()

    def eventFilter(self, obj, event):
        if hasattr(self, 'file_list') and obj == self.file_list.viewport() and event.type() == QEvent.Type.Resize:
            self._update_file_item_texts()
            self._update_project_label()
        return super().eventFilter(obj, event)

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

    def _build_prompt(self, new_project: bool = False, project_root: str | None = None) -> str:
        guide = ""
        if os.path.exists(GUIDE_PATH):
            with open(GUIDE_PATH, 'r', encoding='utf-8') as f:
                guide = f.read().strip()

        task = self.task_input.toPlainText().strip()
        parts = [guide] if guide else []

        root = (project_root or self.project_root).strip()

        if self.files:
            if root:
                parts.append(f"\n## PROJECT ROOT\n\n`{root}`")
            for fp in self.files:
                try:
                    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    ext = os.path.splitext(fp)[1]
                    mode = self.file_modes.get(fp, 'Full')
                    
                    if mode == 'Outline':
                        content = skeletonize_code(content, ext)
                        parts.append(f"\n### `{fp}` (API Outline / References Only)\n```{ext.lstrip('.')}\n{content}\n```")
                    else:
                        if self.chk_minify.isChecked():
                            content = minify_code(content, ext)
                        parts.append(f"\n### `{fp}`\n```{ext.lstrip('.')}\n{content}\n```")
                except Exception as e:
                    parts.append(f"\n### `{fp}`\n[ERROR reading file: {e}]")
        else:
            if root:
                parts.append(
                    "\n## NEW PROJECT ROOT\n\n"
                    f"`{root}`"
                )
            parts.append(
                "\n## NEW PROJECT MODE\n\n"
                "No local source files are loaded yet.\n"
                "Create the project from scratch in the root directory above."
            )

        if new_project and root and not self.files:
            parts.append(
                "\n## NEW PROJECT INSTRUCTIONS\n\n"
                "Treat this as a fresh project scaffold. "
                "Return complete file contents for any new files you create."
            )

        if task:
            parts.append(f"\n---\n## NOW DO THIS\n\n{task}")

        return '\n'.join(parts).strip()

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
            data = {}
            if os.path.exists(SESSION_PATH):
                with open(SESSION_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
        except Exception:
            data = {}
        data['files'] = self.files
        data['project_root'] = self.project_root.strip()
        data['minify'] = self.chk_minify.isChecked()
        data['file_modes'] = self.file_modes
        try:
            with open(SESSION_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving session: {e}", file=sys.stderr)
        self._sync_to_recent_projects()

    def _sync_to_recent_projects(self):
        if not self.files:
            return
        try:
            common = os.path.commonpath(self.files)
            if os.path.isfile(common):
                common = os.path.dirname(common)
            common = os.path.normpath(common)
            
            current_recent = load_recent_details()
            updated = False
            for item in current_recent:
                if os.path.normpath(item["path"]) == common:
                    item["files"] = [os.path.normpath(f) for f in self.files]
                    updated = True
                    break
                    
            if updated:
                save_recent(current_recent)
        except Exception:
            pass

    def _load_session(self):
        import json
        try:
            if os.path.exists(SESSION_PATH):
                with open(SESSION_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                saved = data if isinstance(data, list) else data.get('files', [])
                self.project_root = data.get('project_root', '') if isinstance(data, dict) else ""
                if isinstance(data, dict):
                    self.chk_minify.blockSignals(True)
                    self.chk_minify.setChecked(data.get('minify', False))
                    self.chk_minify.blockSignals(False)
                    self.file_modes = data.get('file_modes', {})
                for fp in saved:
                    if fp not in self.files and os.path.exists(fp):
                        self.files.append(fp)
                        self._add_file_item(fp)
                if self.files:
                    self._update_root()
                    self.status_cb(f"Restored {len(self.files)} file(s) from last session")
                elif self.project_root:
                    self._update_project_label()
        except Exception as e:
            print(f"Error loading session: {e}", file=sys.stderr)

    def _display_path(self, fp: str) -> str:
        root = self.project_root.strip()
        if root:
            try:
                rel = os.path.relpath(fp, root)
                if not rel.startswith('..'):
                    return rel
            except Exception:
                pass
        return os.path.basename(fp)

    def _elide_text(self, text: str, reserve: int = 70) -> str:
        if not hasattr(self, 'file_list'):
            return text
        width = max(100, self.file_list.viewport().width() - reserve)
        return self.fontMetrics().elidedText(text, Qt.TextElideMode.ElideMiddle, width)

    def _update_file_item_texts(self):
        if not hasattr(self, 'file_list'):
            return
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            widget = self.file_list.itemWidget(item)
            if not widget:
                continue
            lbl = widget.findChild(QLabel, "file_path_label")
            if not lbl:
                continue
            fp = item.data(Qt.ItemDataRole.UserRole)
            if not fp:
                continue
            lbl.setText(self._elide_text(self._display_path(fp)))

    def _update_project_label(self):
        if hasattr(self, 'project_path_lbl'):
            if self.project_root:
                self.project_path_lbl.setText(self._elide_text(f"PROJECT ROOT: {self.project_root}", reserve=120))
                self.project_path_lbl.setToolTip(self.project_root)
            else:
                self.project_path_lbl.setText("PROJECT ROOT: <not set>")
                self.project_path_lbl.setToolTip("Choose a directory to use as the project root")

    def _refresh_file_items(self):
        if not hasattr(self, 'file_list'):
            return
        current_files = list(self.files)
        self.file_list.clear()
        for fp in current_files:
            self._add_file_item(fp)

    def _update_root(self):
        if self.root_cb and self.files:
            common = os.path.commonpath(self.files)
            if os.path.isfile(common):
                common = os.path.dirname(common)
            self.project_root = common
            self.root_cb(common)
            self._update_project_label()
            self._refresh_file_items()
            self._update_file_item_texts()

    def _set_project_root(self, d: str, save_recent: bool = True):
        d = os.path.normpath(d)
        self.project_root = d
        if self.root_cb:
            self.root_cb(d)
        self._update_project_label()
        if save_recent:
            add_recent(d, [], [], overwrite_existing=True)
        self._save_session()

    def _add_file_item(self, fp: str):
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, fp) # Store the file path for fast filtering
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        hl = QHBoxLayout(widget)
        hl.setContentsMargins(4, 0, 4, 0)
        hl.setSpacing(4)

        display_path = self._display_path(fp)
        lbl = QLabel(self._elide_text(display_path))
        lbl.setObjectName("file_path_label")
        
        # Smart file size analysis for warning highlights and context limits
        tooltip = [fp]
        try:
            sz_bytes = os.path.getsize(fp)
            sz_kb = sz_bytes / 1024
            if sz_kb > 500:
                lbl_color = CP_RED
                tooltip.append(f"⚠️ DANGER: Very large file ({sz_kb:.1f} KB).")
                tooltip.append("Recommended to exclude or split to prevent LLM context overflow.")
            elif sz_kb > 250:
                lbl_color = CP_YELLOW
                tooltip.append(f"⚠️ WARNING: Large file ({sz_kb:.1f} KB).")
                tooltip.append("May consume significant context window memory.")
            else:
                lbl_color = CP_TEXT
                tooltip.append(f"File size: {sz_kb:.1f} KB")
        except Exception:
            lbl_color = CP_TEXT
            tooltip.append("Could not read file size details")

        lbl.setStyleSheet(f"color: {lbl_color}; background: transparent; font-size: {SOURCE_FILES_FONT_SIZE}pt;")
        lbl.setToolTip("\n".join(tooltip))

        # SVG icon support if configured
        ext = os.path.splitext(fp)[1].lower()
        icon_lbl = None
        if ext in EXTENSION_ICONS:
            icon_value = EXTENSION_ICONS[ext]
            if icon_value:
                pix = render_extension_icon(icon_value, EXTENSION_ICON_SIZE)
                if not pix.isNull():
                    icon_lbl = QLabel()
                    icon_lbl.setPixmap(pix)
                    icon_lbl.setFixedSize(EXTENSION_ICON_SIZE, EXTENSION_ICON_SIZE)
                    icon_lbl.setStyleSheet("background: transparent;")

        mode_combo = QComboBox()
        mode_combo.addItems(["Full", "Outline"])
        mode_combo.setFixedWidth(80)
        mode_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        mode_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                border-radius: 2px;
                padding: 1px 4px;
                font-family: 'Consolas';
                font-size: 8pt;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                selection-background-color: {CP_CYAN};
                selection-color: black;
                border: 1px solid {CP_DIM};
            }}
        """)
        current_mode = self.file_modes.get(fp, 'Full')
        mode_combo.setCurrentText(current_mode)
        mode_combo.currentTextChanged.connect(lambda mode, f=fp: self._on_file_mode_changed(f, mode))

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

        if icon_lbl:
            hl.addWidget(icon_lbl, 0)
        hl.addWidget(lbl, 1)
        hl.addWidget(mode_combo, 0)
        hl.addWidget(btn_rem, 0)

        item_height = max(22, EXTENSION_ICON_SIZE + 4, SOURCE_FILES_FONT_SIZE + 10)
        item.setSizeHint(QSize(100, item_height))
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, widget)
        self._update_file_item_texts()

    def _remove_file(self, fp: str, item: QListWidgetItem):
        if fp in self.files:
            self.files.remove(fp)
        row = self.file_list.row(item)
        if row >= 0:
            self.file_list.takeItem(row)
        self._update_root()
        self._save_session()
        self.status_cb(f"Removed: {os.path.basename(fp)}")

    def _on_file_mode_changed(self, fp: str, mode: str):
        self.file_modes[fp] = mode
        self._save_session()
        self.status_cb(f"Set {os.path.basename(fp)} to {mode}")

    def _set_all_full(self):
        for fp in self.files:
            self.file_modes[fp] = 'Full'
        self._refresh_file_items()
        self._save_session()
        self.status_cb("Set all files to Full mode")

    def _set_all_outline(self):
        for fp in self.files:
            self.file_modes[fp] = 'Outline'
        self._refresh_file_items()
        self._save_session()
        self.status_cb("Set all files to Outline (API Skeleton) mode")

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

        self.project_path_lbl = QLabel("PROJECT ROOT: <not set>")
        self.project_path_lbl.setStyleSheet(
            f"color: {CP_SUB}; font-size: 9pt; font-family: 'Consolas';"
        )
        self.project_path_lbl.setWordWrap(False)
        self.project_path_lbl.setToolTip("Choose a directory to use as the project root")
        vf.addWidget(self.project_path_lbl)

        # File List Search/Filter Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter files by name…")
        self.search_input.textChanged.connect(self._filter_files)
        vf.addWidget(self.search_input)

        # Bulk actions row
        bulk_row = QHBoxLayout()
        bulk_row.setSpacing(4)
        
        self.chk_minify = QCheckBox("Minify (save tokens)")
        self.chk_minify.setChecked(False)
        self.chk_minify.setToolTip("Strips comments and blank lines from full code files to minimize prompt size.")
        self.chk_minify.stateChanged.connect(self._save_session)
        bulk_row.addWidget(self.chk_minify)
        
        bulk_row.addStretch()
        
        lbl_bulk = QLabel("Set all:")
        lbl_bulk.setStyleSheet(f"color: {CP_SUB}; font-size: 8pt;")
        bulk_row.addWidget(lbl_bulk)
        
        btn_bulk_full = QPushButton("FULL")
        btn_bulk_full.setFixedWidth(50)
        btn_bulk_full.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT};
                font-size: 8pt; padding: 2px 4px;
            }}
            QPushButton:hover {{ border-color: {CP_CYAN}; color: {CP_CYAN}; }}
        """)
        btn_bulk_full.clicked.connect(self._set_all_full)
        
        btn_bulk_out = QPushButton("OUTLINE")
        btn_bulk_out.setFixedWidth(65)
        btn_bulk_out.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT};
                font-size: 8pt; padding: 2px 4px;
            }}
            QPushButton:hover {{ border-color: {CP_YELLOW}; color: {CP_YELLOW}; }}
        """)
        btn_bulk_out.clicked.connect(self._set_all_outline)
        
        bulk_row.addWidget(btn_bulk_full)
        bulk_row.addWidget(btn_bulk_out)
        vf.addLayout(bulk_row)

        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.file_list.viewport().installEventFilter(self)
        vf.addWidget(self.file_list)
        left_layout.addWidget(grp_files, 1)

        btn_row = QHBoxLayout()
        btn_add     = QPushButton("＋ ADD FILES")
        btn_add_dir = QPushButton("📁 ADD DIR / ROOT")
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
            self._set_project_root(d)
            self.status_cb(f"Project root set: {d}")
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
        self._set_project_root(d, save_recent=False)
        self.status_cb(f"Added {count} file(s) from directory")
        self._update_root()
        self._save_session()

    def _load_specific_files(self, d: str, files: list[str], extensions: list[str]):
        if not files:
            self._load_all_project_files(d)
            return

        self.files.clear()
        self.file_list.clear()
        
        count = 0
        for fp in files:
            if os.path.exists(fp):
                self.files.append(fp)
                self._add_file_item(fp)
                count += 1
                
        add_recent(d, self.files, extensions, overwrite_existing=False)
        self._set_project_root(d, save_recent=False)
        self.status_cb(f"Loaded {count} saved file(s) for project: {os.path.basename(d)}")
        self._update_root()
        self._save_session()

    def _load_all_project_files(self, d: str):
        self.files.clear()
        self.file_list.clear()
        
        count = 0
        added_files = []
        discovered_exts = set()
        for root, dirs, fnames in os.walk(d):
            dirs[:] = [x for x in dirs if x not in IGNORE_PATTERNS and not x.startswith('.')]
            for fn in fnames:
                ext = os.path.splitext(fn)[1].lower()
                if ext in IGNORE_EXTS:
                    continue
                discovered_exts.add(ext)
                fp = os.path.normpath(os.path.join(root, fn))
                added_files.append(fp)
                if fp not in self.files:
                    self.files.append(fp)
                    self._add_file_item(fp)
                    count += 1
                    
        add_recent(d, added_files, list(discovered_exts), overwrite_existing=True)
        self._set_project_root(d, save_recent=False)
        self.status_cb(f"Re-scanned and loaded {count} file(s) from directory")
        self._update_root()
        self._save_session()

    def _rename_recent(self, path: str):
        from PyQt6.QtWidgets import QInputDialog
        current_name = ""
        items = load_recent_details()
        for item in items:
            if item["path"] == path:
                current_name = item.get("name", "")
                break
        new_name, ok = QInputDialog.getText(self, "Rename Project", "Enter new name (leave empty to show full path):", text=current_name)
        if ok:
            for item in items:
                if item["path"] == path:
                    item["name"] = new_name.strip()
            save_recent(items)
            self.status_cb(f"Renamed: {path}")

    def _show_recent(self):
        btn = self.sender()
        popup = RecentPopup(
            self,
            on_load=self._load_specific_files,
            on_load_all=self._load_all_project_files,
            on_remove=lambda p: (
                remove_recent(p),
                self.status_cb(f"Removed: {p}")
            ),
            on_rename=self._rename_recent
        )
        btn_pos = btn.mapToGlobal(QPoint(0, 0))
        popup_height = popup.sizeHint().height()
        y = btn_pos.y() - popup_height - 2
        if y < 10:
            y = btn_pos.y() + btn.height() + 2
        pos = QPoint(btn_pos.x(), y)
        popup.move(pos)
        popup.show()

    def _clear_files(self):
        self.files.clear()
        self.file_list.clear()
        self._save_session()
        self.status_cb("File list cleared")

    def _generate(self):
        if not self.files and not self.project_root:
            self.status_cb("⚠ Add files or choose a directory first")
            return

        prompt = self._build_prompt()
        if not prompt:
            self.status_cb("⚠ Nothing to generate")
            return

        self.prompt_out.setPlainText(prompt)
        if self.files:
            self.status_cb("Prompt generated — copy and paste into AI")
        else:
            self.status_cb("New project prompt generated — copy and paste into AI")

    def _copy(self):
        text = self.prompt_out.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_cb("✔ Copied to clipboard")
        else:
            self.status_cb("⚠ Nothing to copy — generate first")


def extract_commit_message(text: str) -> str:
    # Try looking for patterns like:
    # - Suggested Commit Message: <msg>
    # - Commit Message: <msg>
    # - git commit -m "<msg>"
    m1 = re.search(r'(?:Suggested\s+)?Commit\s+Message:\s*(.+)', text, re.IGNORECASE)
    if m1:
        return m1.group(1).strip().strip('"`')
    m2 = re.search(r'git\s+commit\s+-m\s+"([^"]+)"', text, re.IGNORECASE)
    if m2:
        return m2.group(1).strip()
    m3 = re.search(r'git\s+commit\s+-m\s+\'([^\']+)\'', text, re.IGNORECASE)
    if m3:
        return m3.group(1).strip()
    return ""


# ── MERGE TAB ─────────────────────────────────────────────────────────────────
class MergeTab(QWidget):
    def __init__(self, status_cb):
        super().__init__()
        self.status_cb = status_cb
        self._parsed_commit_msg = ""
        self._build()
        self._load_prefs()

    def _save_prefs(self):
        import json
        try:
            data = {}
            if os.path.exists(SESSION_PATH):
                with open(SESSION_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
        except Exception:
            data = {}
        data['backup']  = self.chk_backup.isChecked()
        data['preview'] = self.chk_preview.isChecked()
        try:
            with open(SESSION_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving prefs: {e}", file=sys.stderr)

    def _load_prefs(self):
        import json
        try:
            if os.path.exists(SESSION_PATH):
                with open(SESSION_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.chk_backup.blockSignals(True)
                    self.chk_preview.blockSignals(True)
                    if 'backup'  in data: self.chk_backup.setChecked(data['backup'])
                    if 'preview' in data: self.chk_preview.setChecked(data['preview'])
                    self.chk_backup.blockSignals(False)
                    self.chk_preview.blockSignals(False)
        except Exception as e:
            print(f"Error loading prefs: {e}", file=sys.stderr)

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

        self._parsed_commit_msg = extract_commit_message(text)

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

        if ok > 0:
            commit_msg = self._parsed_commit_msg
            if not commit_msg:
                # Fallback commit message generated automatically based on changed files
                successful_files = []
                for r in results:
                    if r.startswith("✔"):
                        parts = r.split("→")
                        if len(parts) > 1:
                            filepath = parts[1].strip()
                            basename = os.path.basename(filepath)
                            if basename not in successful_files:
                                successful_files.append(basename)
                if successful_files:
                    files_str = ", ".join(successful_files[:3])
                    if len(successful_files) > 3:
                        files_str += f" and {len(successful_files) - 3} other(s)"
                    commit_msg = f"update {files_str}"
                else:
                    commit_msg = "update files"

            results.append("\nSuggested Git Commit Command:")
            results.append(f'git commit -m "{commit_msg}"')

        self.result_out.setPlainText('\n'.join(results))
        self.status_cb(f"Done — {ok} applied, {err} failed")
        self._pending_changes = []
        self._parsed_commit_msg = ""

    def _clear(self):
        self.response_input.clear()
        self.result_out.clear()
        self._pending_changes = []
        self._parsed_commit_msg = ""
        self.status_cb("Cleared")


# ── COMMAND TAB ───────────────────────────────────────────────────────────────
class CommandTab(QWidget):
    def __init__(self, status_cb, get_root_fn):
        super().__init__()
        self.status_cb = status_cb
        self.get_root_fn = get_root_fn
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Directory Row
        grp_dir = QGroupBox("WORKING DIRECTORY")
        hd = QHBoxLayout(grp_dir)
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Directory to run command in (defaults to Project Root)…")
        btn_browse = QPushButton("📁 BROWSE")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self._browse_dir)
        hd.addWidget(self.dir_input)
        hd.addWidget(btn_browse)
        layout.addWidget(grp_dir)

        # Command Row
        grp_cmd = QGroupBox("COMMAND INPUT")
        hc = QHBoxLayout(grp_cmd)
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter command (e.g. git status, npm run test)…")
        self.cmd_input.returnPressed.connect(self._run_cmd)
        
        btn_run = QPushButton("▶ RUN COMMAND")
        btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_run.setStyleSheet(f"QPushButton {{ border-color: {CP_CYAN}; color: {CP_CYAN}; }}"
                              f"QPushButton:hover {{ background: {CP_CYAN}; color: #000; border-color: {CP_CYAN}; }}")
        btn_run.clicked.connect(self._run_cmd)

        hc.addWidget(self.cmd_input, 1)
        hc.addWidget(btn_run, 0)
        layout.addWidget(grp_cmd)

        # Results
        grp_res = QGroupBox("COMMAND OUTPUT")
        vr = QVBoxLayout(grp_res)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        vr.addWidget(self.output_text, 1)
        
        btn_copy = QPushButton("📋 COPY OUTPUT")
        btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy.clicked.connect(self._copy_output)
        vr.addWidget(btn_copy)
        
        layout.addWidget(grp_res, 1)

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Working Directory")
        if d:
            self.dir_input.setText(d)

    def _run_cmd(self):
        self.output_text.clear()
        self.status_cb("Running command…")
        
        d = self.dir_input.text().strip()
        if not d:
            d = self.get_root_fn()
            self.dir_input.setText(d)
            
        if not d or not os.path.isdir(d):
            self.status_cb("⚠ Invalid working directory")
            self.output_text.setPlainText("Error: Invalid working directory")
            return
            
        cmd = self.cmd_input.text().strip()
        if not cmd:
            self.status_cb("⚠ Empty command")
            self.output_text.setPlainText("Error: Command is empty")
            return

        import subprocess
        try:
            result = subprocess.run(cmd, cwd=d, shell=True, capture_output=True, text=True, timeout=60)
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                if output: output += "\n"
                output += "--- STDERR ---\n" + result.stderr
                
            if not output:
                output = f"Command completed successfully with exit code {result.returncode} (No output)"
                
            self.output_text.setPlainText(output)
            self.status_cb(f"Command finished with exit code {result.returncode}")
        except subprocess.TimeoutExpired:
            self.output_text.setPlainText("Error: Command timed out after 60 seconds")
            self.status_cb("⚠ Command timed out")
        except Exception as e:
            self.output_text.setPlainText(f"Error running command:\n{str(e)}")
            self.status_cb("⚠ Error running command")

    def _copy_output(self):
        text = self.output_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_cb("✔ Copied output to clipboard")
        else:
            self.status_cb("⚠ Nothing to copy")


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

        btn_settings = QPushButton("⚙ SETTINGS")
        btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_settings.setStyleSheet(f"""
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
        btn_settings.clicked.connect(self._open_settings)

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

        corner_layout.addWidget(btn_settings)
        corner_layout.addWidget(btn_restart)
        self.tabs.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)

        self.merge_tab = MergeTab(self._set_status)
        self.prep_tab  = PrepTab(self._set_status, self.merge_tab.set_root)
        self.command_tab = CommandTab(self._set_status, lambda: self.merge_tab.root_input.text().strip())
        self.tabs.addTab(self.prep_tab,  "⚙  PREP  ( local → AI )")
        self.tabs.addTab(self.merge_tab, "⚡  MERGE  ( AI → local )")
        self.tabs.addTab(self.command_tab, "💻  COMMAND ( runner )")
        root_layout.addWidget(self.tabs)

    def _open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.prep_tab._refresh_file_items()
            self._set_status(f"Settings saved. Applied new font size ({SOURCE_FILES_FONT_SIZE}pt), icon mappings, and icon size ({EXTENSION_ICON_SIZE}px).")

    def _set_status(self, msg: str):
        self.status_bar.showMessage(f"  {msg}")


if __name__ == "__main__":
    load_settings()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
