#!/usr/bin/env python3
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
    QTableWidgetItem, QHeaderView, QSpinBox, QColorDialog, QInputDialog
)
from PyQt6.QtCore import Qt, QPoint, QSize, QEvent, QByteArray
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap

# ── PATH MIGRATION FOR LINUX/MACOS ───────────────────────────────────────────
_original_normpath = os.path.normpath

def _custom_normpath(path):
    if not path:
        return ""
    path_str = str(path)
    if os.name != 'nt':
        # Replace backslashes with forward slashes
        path_str = path_str.replace('\\', '/')
        # If it starts with C:/Users/<username> (case-insensitive), replace it with the Linux user's home directory
        home = os.path.expanduser('~')
        username = os.path.basename(home)
        pattern = r'^[a-zA-Z]:/[uU]sers/' + re.escape(username)
        if re.match(pattern, path_str):
            path_str = re.sub(pattern, home, path_str)
        else:
            # Otherwise, translate the drive letter to home directory (e.g. C:/ -> /home/username/)
            m = re.match(r'^[a-zA-Z]:/', path_str)
            if m:
                path_str = re.sub(r'^[a-zA-Z]:/', home + '/', path_str)
        # Clean up any previously-mangled paths (e.g. /home/nahid/Users/nahid -> /home/nahid)
        mangled_prefix = home + '/Users/' + username
        if path_str.startswith(mangled_prefix):
            path_str = path_str.replace(mangled_prefix, home, 1)
    return _original_normpath(path_str)

os.path.normpath = _custom_normpath

def is_subpath(filepath: str, root_dir: str) -> bool:
    """Return True if filepath is located inside root_dir."""
    if not filepath or not root_dir:
        return False
    try:
        f_norm = os.path.normpath(os.path.abspath(filepath))
        r_norm = os.path.normpath(os.path.abspath(root_dir))
        rel = os.path.relpath(f_norm, r_norm)
        return not rel.startswith('..') and not os.path.isabs(rel)
    except Exception:
        return False


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
QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: #555555; min-height: 20px; border-radius: 4px; }}
QScrollBar::handle:vertical:hover {{ background: #777777; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; width: 0; background: none; }}
QScrollBar:horizontal {{ background: transparent; height: 8px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: #555555; min-width: 20px; border-radius: 4px; }}
QScrollBar::handle:horizontal:hover {{ background: #777777; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ height: 0; width: 0; background: none; }}
QCheckBox {{ spacing: 8px; color: {CP_TEXT}; background: transparent; }}
QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
QSplitter::handle {{ background: {CP_DIM}; }}
QStatusBar {{ background: {CP_PANEL}; color: {CP_SUB}; border-top: 1px solid {CP_DIM}; }}
"""

_HERE        = os.path.dirname(os.path.abspath(__file__))
GUIDE_PATH   = os.path.join(_HERE, "PROMPT_GUIDE.md")
SETTINGS_PATH = os.path.join(_HERE, "settings.json")
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
PROJECT_ICONS = {}
SOURCE_FILES_FONT_SIZE = 9
PROJECTS_FONT_SIZE = 10
PROJECTS_NAME_COLOR = "#FCEE0A"
APP_NAME = "CODE MERGER // CYBERPUNK EDITION"
EXTENSION_ICON_SIZE = 16
SHOW_FILE_MODE_CONTROLS = True
SHOW_PROJECT_PATHS = True
PANEL_WEIGHT_PROJECTS = 260
PANEL_WEIGHT_FILES = 360
PANEL_WEIGHT_PROMPT = 560

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
    global CUSTOM_IGNORED_EXTS, EXTENSION_ICONS, PROJECT_ICONS, SOURCE_FILES_FONT_SIZE, PROJECTS_FONT_SIZE, EXTENSION_ICON_SIZE, SHOW_FILE_MODE_CONTROLS
    global PANEL_WEIGHT_PROJECTS, PANEL_WEIGHT_FILES, PANEL_WEIGHT_PROMPT, PROJECTS_NAME_COLOR, APP_NAME, SHOW_PROJECT_PATHS
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                ignores = data.get('custom_ignored_exts', [])
                CUSTOM_IGNORED_EXTS = set(ignores)
                IGNORE_EXTS.update(CUSTOM_IGNORED_EXTS)
                EXTENSION_ICONS = data.get('extension_icons', {})
                PROJECT_ICONS = data.get('project_icons', {})
                SOURCE_FILES_FONT_SIZE = data.get('source_files_font_size', 9)
                PROJECTS_FONT_SIZE = data.get('projects_font_size', 10)
                PROJECTS_NAME_COLOR = data.get('projects_name_color', '#FCEE0A')
                APP_NAME = data.get('app_name', 'CODE MERGER // CYBERPUNK EDITION')
                EXTENSION_ICON_SIZE = data.get('extension_icon_size', 16)
                SHOW_FILE_MODE_CONTROLS = data.get('show_file_mode_controls', True)
                SHOW_PROJECT_PATHS = data.get('show_project_paths', True)
                PANEL_WEIGHT_PROJECTS = data.get('panel_weight_projects', 260)
                PANEL_WEIGHT_FILES = data.get('panel_weight_files', 360)
                PANEL_WEIGHT_PROMPT = data.get('panel_weight_prompt', 560)
    except Exception as e:
        print(f"Error loading settings: {e}", file=sys.stderr)

def save_settings(ignores: list[str], icons: dict[str, str], font_size: int, proj_font_size: int, icon_size: int, show_file_mode_controls: bool = True, w_projects: int = 260, w_files: int = 360, w_prompt: int = 560, proj_name_color: str = "#FCEE0A", app_name: str = "CODE MERGER // CYBERPUNK EDITION", proj_icons: dict[str, str] = None, show_project_paths: bool = True):
    global CUSTOM_IGNORED_EXTS, EXTENSION_ICONS, PROJECT_ICONS, SOURCE_FILES_FONT_SIZE, PROJECTS_FONT_SIZE, EXTENSION_ICON_SIZE, SHOW_FILE_MODE_CONTROLS
    global PANEL_WEIGHT_PROJECTS, PANEL_WEIGHT_FILES, PANEL_WEIGHT_PROMPT, PROJECTS_NAME_COLOR, APP_NAME, SHOW_PROJECT_PATHS
    CUSTOM_IGNORED_EXTS = set(ignores)
    IGNORE_EXTS.update(CUSTOM_IGNORED_EXTS)
    EXTENSION_ICONS = icons
    if proj_icons is not None:
        PROJECT_ICONS = proj_icons
    SOURCE_FILES_FONT_SIZE = font_size
    PROJECTS_FONT_SIZE = proj_font_size
    PROJECTS_NAME_COLOR = proj_name_color
    APP_NAME = app_name
    EXTENSION_ICON_SIZE = icon_size
    SHOW_FILE_MODE_CONTROLS = show_file_mode_controls
    SHOW_PROJECT_PATHS = show_project_paths
    PANEL_WEIGHT_PROJECTS = w_projects
    PANEL_WEIGHT_FILES = w_files
    PANEL_WEIGHT_PROMPT = w_prompt
    try:
        data = {}
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {}
        data['custom_ignored_exts'] = list(CUSTOM_IGNORED_EXTS)
        data['extension_icons'] = EXTENSION_ICONS
        data['project_icons'] = PROJECT_ICONS
        data['source_files_font_size'] = SOURCE_FILES_FONT_SIZE
        data['projects_font_size'] = PROJECTS_FONT_SIZE
        data['projects_name_color'] = PROJECTS_NAME_COLOR
        data['app_name'] = APP_NAME
        data['extension_icon_size'] = EXTENSION_ICON_SIZE
        data['show_file_mode_controls'] = SHOW_FILE_MODE_CONTROLS
        data['show_project_paths'] = SHOW_PROJECT_PATHS
        data['panel_weight_projects'] = PANEL_WEIGHT_PROJECTS
        data['panel_weight_files'] = PANEL_WEIGHT_FILES
        data['panel_weight_prompt'] = PANEL_WEIGHT_PROMPT
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving settings: {e}", file=sys.stderr)


def load_recent() -> list[str]:
    return [item["path"] for item in load_recent_details()]

def load_recent_details() -> list[dict]:
    try:
        import json
        if not os.path.exists(SETTINGS_PATH):
            return []
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            settings_data = json.load(f)
        if not isinstance(settings_data, dict):
            return []

        projects = settings_data.get('projects', [])
        out = []
        seen = set()
        for p in projects:
            if not isinstance(p, dict):
                continue
            path = p.get("path")
            if not path: continue
            n = os.path.normpath(path)
            if n not in seen:
                seen.add(n)
                out.append({
                    "path": n,
                    "name": p.get("name", ""),
                    "category": p.get("category", ""),
                    "icon": p.get("icon", "") or PROJECT_ICONS.get(n, ""),
                    "files": [os.path.normpath(f) for f in p.get("files", [])],
                    "disabled_files": [os.path.normpath(f) for f in p.get("disabled_files", [])],
                    "extensions": p.get("extensions", []),
                    "clicks": p.get("clicks", 0),
                    "pinned": p.get("pinned", False),
                    "pin_index": p.get("pin_index", 0)
                })
        return out
    except Exception:
        return []

def save_recent(items: list[dict]):
    import json
    try:
        settings_data = {}
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            if not isinstance(settings_data, dict):
                settings_data = {}

        proj_list = []
        for item in items:
            p = os.path.normpath(item["path"])
            entry = {
                "path": p,
                "name": item.get("name", ""),
                "category": item.get("category", ""),
                "icon": item.get("icon", ""),
                "files": [os.path.normpath(f) for f in item.get("files", [])],
                "disabled_files": [os.path.normpath(f) for f in item.get("disabled_files", [])],
                "extensions": item.get("extensions", []),
                "clicks": item.get("clicks", 0),
                "pinned": item.get("pinned", False),
                "pin_index": item.get("pin_index", 0)
            }
            if item.get("icon"):
                PROJECT_ICONS[p] = item["icon"]
            proj_list.append(entry)

        settings_data['projects'] = proj_list
        settings_data['project_icons'] = PROJECT_ICONS
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving recent projects: {e}", file=sys.stderr)

def add_recent(path: str, files: list[str] = None, extensions: list[str] = None, overwrite_existing: bool = False, disabled_files: list[str] = None):
    path = os.path.normpath(path)

    current = load_recent_details()
    
    # Locate existing entry to avoid overwriting previously stored selection details
    existing = None
    for item in current:
        if os.path.normpath(item["path"]) == path:
            existing = item
            break

    name = existing.get("name", "") if existing else ""
    category = existing.get("category", "") if existing else ""
    icon = existing.get("icon", "") if existing else ""
    clicks = existing.get("clicks", 0) if existing else 0
    pinned = existing.get("pinned", False) if existing else False
    pin_index = existing.get("pin_index", 0) if existing else 0
    clicks += 1

    # If overwrite_existing is False, preserve any existing saved selection details
    if not overwrite_existing and existing:
        if existing.get("files"):
            files = existing["files"]
        if existing.get("extensions"):
            extensions = existing["extensions"]
        if disabled_files is None and existing.get("disabled_files"):
            disabled_files = existing["disabled_files"]
    else:
        if not files:
            if existing and existing.get("files"):
                files = existing["files"]
        if not extensions:
            if existing and existing.get("extensions"):
                extensions = existing["extensions"]
        if disabled_files is None and existing and existing.get("disabled_files"):
            disabled_files = existing["disabled_files"]

    if files is None:
        files = []
    if extensions is None:
        extensions = []
    if disabled_files is None:
        disabled_files = []

    normalized_files = [os.path.normpath(f) for f in files]
    normalized_disabled = [os.path.normpath(f) for f in disabled_files]

    # Remove existing entry to move it to the top of the list
    current = [item for item in current if os.path.normpath(item["path"]) != path]
    new_entry = {
        "path": path,
        "files": normalized_files,
        "disabled_files": normalized_disabled,
        "extensions": extensions,
        "clicks": clicks,
        "pinned": pinned,
        "pin_index": pin_index
    }
    if name:
        new_entry["name"] = name
    if category:
        new_entry["category"] = category
    if icon:
        new_entry["icon"] = icon
    current.insert(0, new_entry)
    save_recent(current[:MAX_RECENT])

def remove_recent(path: str):
    target = os.path.normpath(path).lower()
    current = load_recent_details()
    current = [item for item in current if os.path.normpath(item["path"]).lower() != target]
    save_recent(current)

def resequence_pinned_projects(items: list[dict], target_path: str = None, set_pinned: bool = None, target_index: int = None) -> list[dict]:
    """
    Re-sequences all pinned projects to ensure proper contiguous ordering (1, 2, 3...).
    Inserts target_path at target_index, shifting existing pinned items and filling any gaps.
    """
    norm_target = os.path.normpath(target_path) if target_path else None

    pinned_list = []
    unpinned_list = []

    for item in items:
        p_norm = os.path.normpath(item["path"])
        if norm_target and p_norm == norm_target:
            if set_pinned is not None:
                item["pinned"] = set_pinned
            if target_index is not None and set_pinned:
                item["pin_index"] = target_index

        if item.get("pinned", False):
            pinned_list.append(item)
        else:
            item["pinned"] = False
            item["pin_index"] = 0
            unpinned_list.append(item)

    # Sort existing pinned items by current pin_index
    pinned_list.sort(key=lambda x: x.get("pin_index", 1))

    # If target_path is being pinned or re-indexed, place it at position target_index - 1
    if norm_target and set_pinned:
        target_item = next((x for x in pinned_list if os.path.normpath(x["path"]) == norm_target), None)
        if target_item:
            pinned_list.remove(target_item)
            idx_pos = max(0, min(len(pinned_list), (target_index or 1) - 1))
            pinned_list.insert(idx_pos, target_item)

    # Re-assign strictly contiguous 1-based indices (1, 2, 3...)
    for idx, item in enumerate(pinned_list, start=1):
        item["pinned"] = True
        item["pin_index"] = idx

    return items


# ── MERGE LOGIC ───────────────────────────────────────────────────────────────
_TOKENS = r'(@@FILE:|@@MODE:|@@TO:|@@FROM:|@@AFTER:|@@INSERT:|@@END)'

def _normalize(text: str) -> str:
    """Normalize AI response: strip markdown fences, ensure @@ tokens are on their own lines."""
    text = text.replace('\r\n', '\n')

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


def fuzzy_replace_block(content: str, from_block: str, to_block: str, threshold: float = 0.70) -> str | None:
    if from_block in content:
        return content.replace(from_block, to_block, 1)

    lines_content = content.splitlines(keepends=True)
    lines_content_raw = [l.strip() for l in content.splitlines()]
    lines_from_raw = [l.strip() for l in from_block.splitlines()]

    if not lines_from_raw:
        return None

    n_from = len(lines_from_raw)
    for i in range(len(lines_content_raw) - n_from + 1):
        slice_raw = lines_content_raw[i : i + n_from]
        if slice_raw == lines_from_raw:
            target_substr = "".join(lines_content[i : i + n_from])
            return content.replace(target_substr, to_block, 1)

    import difflib
    best_ratio = 0.0
    best_range = None

    for window_len in range(max(1, n_from - 2), n_from + 3):
        for i in range(len(lines_content) - window_len + 1):
            slice_str = "".join(lines_content[i : i + window_len])
            matcher = difflib.SequenceMatcher(None, slice_str, from_block)
            ratio = matcher.ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_range = (i, i + window_len)

    if best_ratio >= threshold and best_range is not None:
        start_idx, end_idx = best_range
        target_substr = "".join(lines_content[start_idx:end_idx])
        return content.replace(target_substr, to_block, 1)

    return None


def fuzzy_find_anchor(content: str, anchor: str, threshold: float = 0.70) -> str | None:
    if anchor in content:
        return anchor

    lines_content = content.splitlines(keepends=True)
    lines_content_raw = [l.strip() for l in content.splitlines()]
    lines_anchor_raw = [l.strip() for l in anchor.splitlines()]

    if not lines_anchor_raw:
        return None

    n_anchor = len(lines_anchor_raw)
    for i in range(len(lines_content_raw) - n_anchor + 1):
        slice_raw = lines_content_raw[i : i + n_anchor]
        if slice_raw == lines_anchor_raw:
            return "".join(lines_content[i : i + n_anchor])

    import difflib
    best_ratio = 0.0
    best_range = None

    for window_len in range(max(1, n_anchor - 2), n_anchor + 3):
        for i in range(len(lines_content) - window_len + 1):
            slice_str = "".join(lines_content[i : i + window_len])
            matcher = difflib.SequenceMatcher(None, slice_str, anchor)
            ratio = matcher.ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_range = (i, i + window_len)

    if best_ratio >= threshold and best_range is not None:
        start_idx, end_idx = best_range
        return "".join(lines_content[start_idx:end_idx])

    return None


def apply_changes(changes: list[dict], root: str, backup: bool, match_mode: str = "exact") -> list[str]:
    """Apply parsed changes. Returns list of result messages."""
    results = []
    is_fuzzy = (match_mode == "fuzzy")
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
                    content = f.read().replace('\r\n', '\n')

                target_from = ch["from"].replace('\r\n', '\n')
                target_to = ch["to"].replace('\r\n', '\n')

                if is_fuzzy:
                    new_content = fuzzy_replace_block(content, target_from, target_to)
                    if new_content is not None:
                        if backup:
                            _backup(fpath)
                        with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                            f.write(new_content)
                        results.append(f"✔ replace_block (fuzzy) → {ch['file']}")
                        continue

                if target_from not in content:
                    try:
                        failure_info = analyze_match_failure(content, target_from, "replace_block")
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
                with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content.replace(target_from, target_to, 1))
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

                anchor_target = None
                if is_fuzzy:
                    anchor_target = fuzzy_find_anchor(content, ch["after"])
                elif ch["after"] in content:
                    anchor_target = ch["after"]

                if not anchor_target:
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
                new = content.replace(anchor_target, anchor_target + '\n' + ch["insert"], 1)
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new)
                tag = "insert_after (fuzzy)" if is_fuzzy and anchor_target != ch["after"] else "insert_after"
                results.append(f"✔ {tag}  → {ch['file']}")

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

                if is_fuzzy:
                    new_content = fuzzy_replace_block(content, ch["from"], "")
                    if new_content is not None:
                        if backup:
                            _backup(fpath)
                        with open(fpath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        results.append(f"✔ delete_block (fuzzy)  → {ch['file']}")
                        continue

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
            if os.path.exists(SETTINGS_PATH):
                import json
                with open(SETTINGS_PATH, 'r') as f:
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
            btn_open.setToolTip("Open project folder in File Manager")
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
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, 'r') as f:
                    data = json.load(f)
            if not isinstance(data, dict):
                data = {}
            data['recent_sort_mode'] = self.sort_mode
            with open(SETTINGS_PATH, 'w') as f:
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
            elif sys.platform.startswith('darwin'):
                import subprocess
                subprocess.Popen(['open', p])
            else:
                import subprocess
                subprocess.Popen(['xdg-open', p])
        except Exception:
            pass


# ── EXTENSION SELECTOR DIALOG ────────────────────────────────────────────────
# ── EDIT PROJECT DIALOG ─────────────────────────────────────────────────────
class EditProjectDialog(QDialog):
    """Unified modal dialog to edit project alias name, category, icon, pin status/index, and manage hidden files."""
    def __init__(self, path: str, name: str, category: str, icon: str, disabled_files: list[str], pinned: bool = False, pin_index: int = 1, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏️ EDIT PROJECT DETAILS")
        self.resize(560, 520)
        self.setStyleSheet(THEME)
        self.path = path
        self.disabled_files = list(disabled_files)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Path Read-only label
        lbl_path = QLabel(f"Project Path: {path}")
        lbl_path.setWordWrap(True)
        lbl_path.setStyleSheet(f"color: {CP_SUB}; font-size: 8.5pt;")
        layout.addWidget(lbl_path)

        # Name input
        h_name = QHBoxLayout()
        lbl_n = QLabel("Project Alias:")
        lbl_n.setFixedWidth(110)
        lbl_n.setStyleSheet(f"color: {CP_TEXT}; font-weight: bold;")
        self.input_name = QLineEdit(name)
        self.input_name.setPlaceholderText("Custom display name…")
        h_name.addWidget(lbl_n)
        h_name.addWidget(self.input_name)
        layout.addLayout(h_name)

        # Category input
        h_cat = QHBoxLayout()
        lbl_c = QLabel("Category / Tags:")
        lbl_c.setFixedWidth(110)
        lbl_c.setStyleSheet(f"color: {CP_TEXT}; font-weight: bold;")
        self.input_cat = QLineEdit(category)
        self.input_cat.setPlaceholderText("e.g. Frontend, Tools, Python, AI…")
        h_cat.addWidget(lbl_c)
        h_cat.addWidget(self.input_cat)
        layout.addLayout(h_cat)

        # Custom Icon input + preview
        h_icon = QHBoxLayout()
        lbl_i = QLabel("Custom Icon:")
        lbl_i.setFixedWidth(110)
        lbl_i.setStyleSheet(f"color: {CP_TEXT}; font-weight: bold;")

        self.input_icon = QLineEdit(icon)
        self.input_icon.setPlaceholderText("Emoji, Nerd Font, or SVG XML snippet…")

        self.icon_preview = QLabel()
        self.icon_preview.setFixedSize(24, 24)
        self.icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_preview.setStyleSheet("background: transparent;")
        self.icon_preview.setPixmap(render_extension_icon(icon, 20))

        self.input_icon.textChanged.connect(lambda text: self.icon_preview.setPixmap(render_extension_icon(text, 20)))

        h_icon.addWidget(lbl_i)
        h_icon.addWidget(self.input_icon, 1)
        h_icon.addWidget(self.icon_preview, 0)
        layout.addLayout(h_icon)

        # Pin Settings Row
        h_pin = QHBoxLayout()
        lbl_p = QLabel("Pin Settings:")
        lbl_p.setFixedWidth(110)
        lbl_p.setStyleSheet(f"color: {CP_TEXT}; font-weight: bold;")

        self.chk_pinned = QCheckBox("Pin to top")
        self.chk_pinned.setChecked(pinned)
        self.chk_pinned.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")

        lbl_idx = QLabel("Pin Index:")
        lbl_idx.setStyleSheet(f"color: {CP_TEXT}; margin-left: 10px;")

        self.spin_pin_index = QSpinBox()
        self.spin_pin_index.setRange(1, 999)
        self.spin_pin_index.setValue(pin_index if pin_index >= 1 else 1)
        self.spin_pin_index.setStyleSheet(f"""
            QSpinBox {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 4px;
            }}
        """)
        self.spin_pin_index.setEnabled(pinned)
        self.chk_pinned.toggled.connect(self.spin_pin_index.setEnabled)

        h_pin.addWidget(lbl_p)
        h_pin.addWidget(self.chk_pinned)
        h_pin.addWidget(lbl_idx)
        h_pin.addWidget(self.spin_pin_index)
        h_pin.addStretch()
        layout.addLayout(h_pin)

        # Hidden / Disabled Files Manager
        grp_files = QGroupBox("HIDDEN / DISABLED FILES IN THIS PROJECT")
        v_gf = QVBoxLayout(grp_files)

        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(140)
        self.file_list.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM};")

        if self.disabled_files:
            for df in self.disabled_files:
                is_ext = not is_subpath(df, self.path)
                if is_ext:
                    li = QListWidgetItem(f"⚠️  [OUTSIDE PROJECT] {df}")
                    li.setForeground(QColor(CP_RED))
                else:
                    try:
                        rel_p = os.path.relpath(df, self.path)
                    except Exception:
                        rel_p = os.path.basename(df)
                    li = QListWidgetItem(f"🚫  {rel_p}")
                li.setToolTip(df)
                li.setData(Qt.ItemDataRole.UserRole, df)
                self.file_list.addItem(li)
        else:
            li = QListWidgetItem("No hidden/disabled files for this project.")
            li.setFlags(Qt.ItemFlag.NoItemFlags)
            self.file_list.addItem(li)

        v_gf.addWidget(self.file_list)

        btn_box = QHBoxLayout()
        btn_unhide = QPushButton("✔ Un-hide Selected File")
        btn_unhide.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_unhide.setStyleSheet(f"background-color: {CP_DIM}; font-size: 8.5pt;")
        btn_unhide.clicked.connect(self._unhide_selected)

        btn_purge_ext = QPushButton("🗑️ Purge External Files")
        btn_purge_ext.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_purge_ext.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_RED}; color: {CP_RED}; font-size: 8.5pt;")
        btn_purge_ext.clicked.connect(self._purge_external_files)

        btn_box.addWidget(btn_unhide)
        btn_box.addWidget(btn_purge_ext)
        v_gf.addLayout(btn_box)

        layout.addWidget(grp_files)

        # Buttons
        btn_row = QHBoxLayout()
        btn_ok = QPushButton("✔ SAVE DETAILS")
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

    def _unhide_selected(self):
        curr = self.file_list.currentItem()
        if curr:
            fp = curr.data(Qt.ItemDataRole.UserRole)
            if fp and fp in self.disabled_files:
                self.disabled_files.remove(fp)
                self.file_list.takeItem(self.file_list.row(curr))

    def _purge_external_files(self):
        to_remove = [df for df in self.disabled_files if not is_subpath(df, self.path)]
        for df in to_remove:
            self.disabled_files.remove(df)
        self.file_list.clear()
        if self.disabled_files:
            for df in self.disabled_files:
                try:
                    rel_p = os.path.relpath(df, self.path)
                except Exception:
                    rel_p = os.path.basename(df)
                li = QListWidgetItem(f"🚫  {rel_p}")
                li.setToolTip(df)
                li.setData(Qt.ItemDataRole.UserRole, df)
                self.file_list.addItem(li)
        else:
            li = QListWidgetItem("No hidden/disabled files for this project.")
            li.setFlags(Qt.ItemFlag.NoItemFlags)
            self.file_list.addItem(li)


    def get_details(self) -> tuple[str, str, str, list[str], bool, int]:
        return (
            self.input_name.text().strip(),
            self.input_cat.text().strip(),
            self.input_icon.text().strip(),
            self.disabled_files,
            self.chk_pinned.isChecked(),
            self.spin_pin_index.value()
        )

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
        self.proj_icons = dict(PROJECT_ICONS)
        self.font_size = SOURCE_FILES_FONT_SIZE
        self.proj_font_size = PROJECTS_FONT_SIZE
        self.proj_name_color = PROJECTS_NAME_COLOR
        self.app_name = APP_NAME
        self.icon_size = EXTENSION_ICON_SIZE
        self.show_file_mode_controls = SHOW_FILE_MODE_CONTROLS
        self.show_project_paths = SHOW_PROJECT_PATHS
        self.w_projects = PANEL_WEIGHT_PROJECTS
        self.w_files = PANEL_WEIGHT_FILES
        self.w_prompt = PANEL_WEIGHT_PROMPT

        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.tabs = QTabWidget()

        # --- TAB 1: DISPLAY SIZES ---
        tab_font = QWidget()
        v_font = QVBoxLayout(tab_font)
        v_font.setContentsMargins(8, 8, 8, 8)
        v_font.setSpacing(12)

        lbl_font = QLabel("Adjust display settings:")
        lbl_font.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        v_font.addWidget(lbl_font)

        # Custom Application / GUI Name
        h_app_name = QHBoxLayout()
        lbl_an = QLabel("Application / GUI Name:")
        lbl_an.setStyleSheet(f"color: {CP_TEXT};")
        self.input_app_name = QLineEdit(self.app_name)
        self.input_app_name.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;")
        h_app_name.addWidget(lbl_an)
        h_app_name.addWidget(self.input_app_name, 1)
        v_font.addLayout(h_app_name)


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

        lbl_pfs = QLabel("Projects Font Size (pt):")
        lbl_pfs.setStyleSheet(f"color: {CP_TEXT}; margin-left: 14px;")

        self.spin_pfs = QSpinBox()
        self.spin_pfs.setRange(6, 24)
        self.spin_pfs.setValue(self.proj_font_size)
        self.spin_pfs.setStyleSheet(f"""
            QSpinBox {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 4px;
            }}
        """)
        h_font_settings.addWidget(lbl_pfs)
        h_font_settings.addWidget(self.spin_pfs)
        h_font_settings.addStretch()

        v_font.addLayout(h_font_settings)

        # Combined Color Picker & Preview Button
        h_color_settings = QHBoxLayout()
        lbl_pcolor = QLabel("Projects Name Text Color:")
        lbl_pcolor.setStyleSheet(f"color: {CP_TEXT};")

        self.btn_pick_color = QPushButton()
        self.btn_pick_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pick_color.clicked.connect(self._choose_proj_color)
        self._update_color_button_style()

        h_color_settings.addWidget(lbl_pcolor)
        h_color_settings.addWidget(self.btn_pick_color)
        h_color_settings.addStretch()

        v_font.addLayout(h_color_settings)

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

        # File mode controls visibility
        self.chk_show_mode = QCheckBox("Show Full / Outline controls and Minify option in PREP tab")
        self.chk_show_mode.setChecked(self.show_file_mode_controls)
        self.chk_show_mode.setStyleSheet(f"color: {CP_TEXT};")
        self.chk_show_mode.setToolTip("When unchecked, the Full/Outline selector per file and the\nMinify / Set-all toolbar are hidden to save space.")
        v_font.addWidget(self.chk_show_mode)

        # Show / Hide Project Directory Paths
        self.chk_show_proj_paths = QCheckBox("Show directory paths under project names in Projects panel")
        self.chk_show_proj_paths.setChecked(self.show_project_paths)
        self.chk_show_proj_paths.setStyleSheet(f"color: {CP_TEXT};")
        self.chk_show_proj_paths.setToolTip("Uncheck to hide directory paths under project names in the sidebar.")
        v_font.addWidget(self.chk_show_proj_paths)


        # ── PANEL WIDTH WEIGHTS SECTION ──
        lbl_panels = QLabel("Panel Initial Widths (px):")
        lbl_panels.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; margin-top: 10px;")
        v_font.addWidget(lbl_panels)

        h_panels = QHBoxLayout()
        h_panels.setSpacing(12)

        # Projects Panel Width
        v_p1 = QVBoxLayout()
        lbl_p1 = QLabel("Projects Panel:")
        lbl_p1.setStyleSheet(f"color: {CP_TEXT}; font-size: 8.5pt;")
        self.spin_w_proj = QSpinBox()
        self.spin_w_proj.setRange(100, 1000)
        self.spin_w_proj.setValue(self.w_projects)
        self.spin_w_proj.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;")
        v_p1.addWidget(lbl_p1)
        v_p1.addWidget(self.spin_w_proj)

        # Source Files Panel Width
        v_p2 = QVBoxLayout()
        lbl_p2 = QLabel("Source Files Panel:")
        lbl_p2.setStyleSheet(f"color: {CP_TEXT}; font-size: 8.5pt;")
        self.spin_w_files = QSpinBox()
        self.spin_w_files.setRange(100, 1000)
        self.spin_w_files.setValue(self.w_files)
        self.spin_w_files.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;")
        v_p2.addWidget(lbl_p2)
        v_p2.addWidget(self.spin_w_files)

        # Prompt Panel Width
        v_p3 = QVBoxLayout()
        lbl_p3 = QLabel("Task / Prompt Panel:")
        lbl_p3.setStyleSheet(f"color: {CP_TEXT}; font-size: 8.5pt;")
        self.spin_w_prompt = QSpinBox()
        self.spin_w_prompt.setRange(100, 2000)
        self.spin_w_prompt.setValue(self.w_prompt)
        self.spin_w_prompt.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;")
        v_p3.addWidget(lbl_p3)
        v_p3.addWidget(self.spin_w_prompt)

        h_panels.addLayout(v_p1)
        h_panels.addLayout(v_p2)
        h_panels.addLayout(v_p3)
        h_panels.addStretch()

        v_font.addLayout(h_panels)

        v_font.addStretch()

        self.tabs.addTab(tab_font, "🅰 DISPLAY SIZES")

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

        self.form_preview = QLabel()
        self.form_preview.setFixedSize(24, 24)
        self.form_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_preview.setStyleSheet(f"border: 1px solid {CP_DIM}; background-color: {CP_BG};")
        self.input_icon.textChanged.connect(self._update_form_preview)

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
        form_layout.addWidget(self.form_preview, 0)
        form_layout.addWidget(btn_form_add, 0)

        v_icons.addWidget(form_widget)

        # Table of icons (with Preview column)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Extension", "Icon Value", "Preview"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(2, 60)
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

        # --- TAB 3: PROJECT ICONS ---
        tab_proj_icons = QWidget()
        v_picons = QVBoxLayout(tab_proj_icons)
        v_picons.setContentsMargins(8, 8, 8, 8)
        v_picons.setSpacing(8)

        lbl_picons = QLabel("Assign custom SVG icons, Emojis, or Nerd Fonts to individual projects:")
        lbl_picons.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        v_picons.addWidget(lbl_picons)

        self.proj_icon_table = QTableWidget(0, 3)
        self.proj_icon_table.setHorizontalHeaderLabels(["Project Name / Path", "Custom Icon (SVG/Emoji)", "Preview"])
        self.proj_icon_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.proj_icon_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.proj_icon_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.proj_icon_table.setColumnWidth(0, 200)
        self.proj_icon_table.setColumnWidth(2, 60)
        self.proj_icon_table.setStyleSheet(f"""
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
        """)
        v_picons.addWidget(self.proj_icon_table)

        # Populate project icon table
        recent_projs = load_recent_details()
        for p_item in recent_projs:
            p_path = p_item["path"]
            p_name = p_item.get("name") or os.path.basename(p_path) or p_path
            norm_p = os.path.normpath(p_path)
            curr_icon = self.proj_icons.get(norm_p, "")
            self._insert_proj_icon_row(norm_p, p_name, curr_icon)

        self.tabs.addTab(tab_proj_icons, "📁 PROJECT ICONS")


        # Populate table
        for ext, icon_val in sorted(self.icons.items()):
            self._insert_table_row(ext, icon_val)

        # --- TAB 3: IGNORE LIST ---
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

    def _update_form_preview(self, text: str):
        pix = render_extension_icon(text, 20)
        self.form_preview.setPixmap(pix)

    def _choose_proj_color(self):
        initial = QColor(self.proj_name_color or "#FCEE0A")
        color = QColorDialog.getColor(initial, self, "Select Project Name Color")
        if color.isValid():
            self.proj_name_color = color.name()
            self._update_color_button_style()

    def _update_color_button_style(self):
        hex_code = (self.proj_name_color or "#FCEE0A").upper()
        col = QColor(hex_code)
        lum = (0.299 * col.red() + 0.587 * col.green() + 0.114 * col.blue()) if col.isValid() else 255
        text_col = "#000000" if lum > 128 else "#FFFFFF"
        self.btn_pick_color.setText(f"🎨  {hex_code}")
        self.btn_pick_color.setStyleSheet(f"""
            QPushButton {{
                background-color: {hex_code};
                color: {text_col};
                border: 1px solid {CP_DIM};
                font-family: 'Consolas';
                font-weight: bold;
                font-size: 9.5pt;
                padding: 4px 14px;
            }}
            QPushButton:hover {{
                border-color: {CP_CYAN};
            }}
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

        # 3rd Column: Live Preview Label
        preview_lbl = QLabel()
        preview_lbl.setFixedSize(24, 24)
        preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_lbl.setStyleSheet("background: transparent;")
        
        # Initial render
        pix = render_extension_icon(icon_value, 20)
        preview_lbl.setPixmap(pix)
        
        self.table.setCellWidget(row, 2, preview_lbl)

        # Update preview whenever input text changes
        val_input.textChanged.connect(lambda text, lbl=preview_lbl: lbl.setPixmap(render_extension_icon(text, 20)))

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

    def _insert_proj_icon_row(self, path: str, name: str, icon_value: str = ""):
        row = self.proj_icon_table.rowCount()
        self.proj_icon_table.insertRow(row)

        name_item = QTableWidgetItem(name)
        name_item.setToolTip(path)
        name_item.setData(Qt.ItemDataRole.UserRole, path)
        name_item.setFont(QFont("Consolas", 10))
        self.proj_icon_table.setItem(row, 0, name_item)

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
        self.proj_icon_table.setCellWidget(row, 1, widget)

        preview_lbl = QLabel()
        preview_lbl.setFixedSize(24, 24)
        preview_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_lbl.setStyleSheet("background: transparent;")
        preview_lbl.setPixmap(render_extension_icon(icon_value, 20))
        self.proj_icon_table.setCellWidget(row, 2, preview_lbl)

        val_input.textChanged.connect(lambda text, lbl=preview_lbl: lbl.setPixmap(render_extension_icon(text, 20)))

    def _get_proj_icon_mappings(self) -> dict[str, str]:
        mappings = {}
        for row in range(self.proj_icon_table.rowCount()):
            item = self.proj_icon_table.item(row, 0)
            if not item:
                continue
            path = item.data(Qt.ItemDataRole.UserRole)
            if not path:
                continue
            cell_widget = self.proj_icon_table.cellWidget(row, 1)
            if cell_widget:
                inp = cell_widget.findChild(QLineEdit)
                val = inp.text().strip() if inp else ""
                if val:
                    mappings[os.path.normpath(path)] = val
        return mappings


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
        proj_icons = self._get_proj_icon_mappings()
        font_size = self.spin_fs.value()
        proj_font_size = self.spin_pfs.value()
        proj_color = self.proj_name_color or "#FCEE0A"
        app_name = self.input_app_name.text().strip() or "CODE MERGER // CYBERPUNK EDITION"
        icon_size = self.spin_is.value()
        show_mode = self.chk_show_mode.isChecked()
        show_proj_paths = self.chk_show_proj_paths.isChecked()
        w_proj = self.spin_w_proj.value()
        w_files = self.spin_w_files.value()
        w_prompt = self.spin_w_prompt.value()

        save_settings(ignores, icons, font_size, proj_font_size, icon_size, show_mode, w_proj, w_files, w_prompt, proj_color, app_name, proj_icons, show_proj_paths)
        self.accept()


# ── PREP TAB ──────────────────────────────────────────────────────────────────
class PrepTab(QWidget):
    def __init__(self, status_cb, root_cb=None):
        super().__init__()
        self.status_cb = status_cb
        self.root_cb = root_cb
        self.files: list[str] = []
        self.file_modes: dict[str, str] = {}
        self.disabled_files: set[str] = set()
        self.project_root = ""
        self._sort_mode: str = "none"   # "none" | "ext" | "name"
        self.setAcceptDrops(True) # Enable Drag & Drop support for files and folders
        self._build()
        self._load_session()
        self._populate_projects()

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
                if fp in self.disabled_files:
                    continue  # Skip disabled files
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
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
        except Exception:
            data = {}

        data['active_session'] = {
            'files': self.files,
            'project_root': self.project_root.strip(),
            'minify': self.chk_minify.isChecked(),
            'file_modes': self.file_modes,
            'disabled_files': list(self.disabled_files)
        }

        try:
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving session: {e}", file=sys.stderr)
        self._sync_to_recent_projects()

    def apply_panel_sizes(self):
        if hasattr(self, 'splitter'):
            self.splitter.setSizes([PANEL_WEIGHT_PROJECTS, PANEL_WEIGHT_FILES, PANEL_WEIGHT_PROMPT])


    def _sync_to_recent_projects(self):
        if not self.files and not self.project_root:
            return
        try:
            common = os.path.normpath(self.project_root) if self.project_root else os.path.normpath(os.path.commonpath(self.files))
            
            current_recent = load_recent_details()
            updated = False
            for item in current_recent:
                if os.path.normpath(item["path"]) == common:
                    item["files"] = [os.path.normpath(f) for f in self.files]
                    item["disabled_files"] = [os.path.normpath(f) for f in self.disabled_files]
                    updated = True
                    break

            if not updated and self.project_root:
                # Add new entry for active root if not in recent
                current_recent.insert(0, {
                    "path": common,
                    "files": [os.path.normpath(f) for f in self.files],
                    "disabled_files": [os.path.normpath(f) for f in self.disabled_files],
                    "extensions": [],
                    "clicks": 1
                })
                updated = True

            if updated:
                save_recent(current_recent)
        except Exception:
            pass

    def _load_session(self):
        import json
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    return
                session = data.get('active_session', {})
                if isinstance(session, dict):
                    saved = session.get('files', [])
                    self.project_root = session.get('project_root', '')
                    self.chk_minify.blockSignals(True)
                    self.chk_minify.setChecked(session.get('minify', False))
                    self.chk_minify.blockSignals(False)
                    self.file_modes = session.get('file_modes', {})
                    self.disabled_files = set(session.get('disabled_files', []))
                    for fp in saved:
                        norm_fp = os.path.normpath(fp)
                        if norm_fp not in self.files and os.path.exists(norm_fp):
                            self.files.append(norm_fp)
                            self._add_file_item(norm_fp)
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
                elided = self.fontMetrics().elidedText(self.project_root, Qt.TextElideMode.ElideMiddle, max(50, self.project_path_lbl.width()))
                self.project_path_lbl.setText(elided)
                self.project_path_lbl.setToolTip(self.project_root)
                self.project_path_lbl.setStyleSheet("color: lightgreen; font-size: 9pt; font-family: 'Consolas';")
            else:
                self.project_path_lbl.setText("<not set>")
                self.project_path_lbl.setToolTip("Choose a directory to use as the project root")
                self.project_path_lbl.setStyleSheet("color: lightgreen; font-size: 9pt; font-family: 'Consolas';")

    def _refresh_file_items(self):
        if not hasattr(self, 'file_list'):
            return
        # Rebuild with enabled files first, disabled files at the end
        enabled = [fp for fp in self.files if fp not in self.disabled_files]
        disabled = [fp for fp in self.files if fp in self.disabled_files]
        self.file_list.clear()
        for fp in enabled + disabled:
            self._add_file_item(fp)

    def _update_root(self):
        if not self.files:
            return
        if not self.project_root:
            try:
                common = os.path.commonpath(self.files)
                if os.path.isfile(common):
                    common = os.path.dirname(common)
                self.project_root = common
            except Exception:
                pass
        if self.root_cb and self.project_root:
            self.root_cb(self.project_root)
        self._update_project_label()
        self._refresh_file_items()
        self._update_file_item_texts()

    def _set_project_root(self, d: str, save_recent: bool = True):
        d = os.path.normpath(d)
        self.project_root = d
        # Purge any external files outside the project root
        self.files = [f for f in self.files if is_subpath(f, d)]
        self.disabled_files = {f for f in self.disabled_files if is_subpath(f, d)}
        if self.root_cb:
            self.root_cb(d)
        self._update_project_label()
        if save_recent:
            add_recent(d, self.files, [], overwrite_existing=True)
        self._save_session()
        self._update_active_project_highlight()

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
        mode_combo.setVisible(SHOW_FILE_MODE_CONTROLS)

        # Toggle button: green dot = enabled, grey dot = disabled
        is_disabled = fp in self.disabled_files
        btn_toggle = QPushButton("⬤")
        btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_toggle.setFixedWidth(22)
        btn_toggle.setFixedHeight(18)
        btn_toggle.setToolTip("Click to disable this file (exclude from prompt)\nRight-click to remove it from the list")
        self._apply_toggle_style(btn_toggle, not is_disabled)
        btn_toggle.clicked.connect(lambda _, f=fp, b=btn_toggle, w=widget, lb=lbl, mc=mode_combo: self._toggle_file(f, b, w, lb, mc))

        # Token estimate label
        try:
            sz_bytes = os.path.getsize(fp)
            tokens = int(sz_bytes / 3.5)
            if tokens >= 1000:
                tok_text = f"{tokens/1000:.1f}k"
            else:
                tok_text = str(tokens)
        except Exception:
            tok_text = "?"
        tok_lbl = QLabel(tok_text)
        tok_lbl.setFixedWidth(40)
        tok_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        tok_lbl.setStyleSheet(f"color: {CP_SUB}; background: transparent; font-family: 'Consolas'; font-size: 8pt;")
        tok_lbl.setToolTip(f"Estimated token count (file size / 3.5)")

        # Apply initial dimmed state if disabled
        if is_disabled:
            lbl.setStyleSheet(f"color: {CP_SUB}; background: transparent; font-size: {SOURCE_FILES_FONT_SIZE}pt; text-decoration: line-through;")
            mode_combo.setEnabled(False)

        if icon_lbl:
            hl.addWidget(icon_lbl, 0)
        hl.addWidget(lbl, 1)
        hl.addWidget(mode_combo, 0)
        hl.addWidget(tok_lbl, 0)
        hl.addWidget(btn_toggle, 0)

        # Right-click on the widget row → context menu to remove
        widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        widget.customContextMenuRequested.connect(lambda pos, f=fp, it=item: self._file_item_context_menu(f, it, pos, widget))

        item_height = max(22, EXTENSION_ICON_SIZE + 4, SOURCE_FILES_FONT_SIZE + 10)
        item.setSizeHint(QSize(100, item_height))
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, widget)
        self._update_file_item_texts()

    def _remove_file(self, fp: str, item: QListWidgetItem):
        if fp in self.files:
            self.files.remove(fp)
        if fp in self.disabled_files:
            self.disabled_files.discard(fp)
        row = self.file_list.row(item)
        if row >= 0:
            self.file_list.takeItem(row)
        self._update_root()
        self._save_session()
        self.status_cb(f"Removed: {os.path.basename(fp)}")

    def _apply_toggle_style(self, btn: QPushButton, enabled: bool):
        if enabled:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none; color: {CP_GREEN};
                    padding: 0; font-size: 10pt;
                }}
                QPushButton:hover {{ color: #00cc1a; }}
            """)
            btn.setToolTip("Enabled — click to disable (exclude from prompt)\nRight-click row to remove from list")
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none; color: {CP_DIM};
                    padding: 0; font-size: 10pt;
                }}
                QPushButton:hover {{ color: {CP_SUB}; }}
            """)
            btn.setToolTip("Disabled — file excluded from prompt\nClick to re-enable  |  Right-click row to remove from list")

    def _toggle_file(self, fp: str, btn: QPushButton, widget: QWidget, lbl: QLabel, mode_combo: QComboBox):
        is_currently_disabled = fp in self.disabled_files
        if is_currently_disabled:
            self.disabled_files.discard(fp)
            self._apply_toggle_style(btn, True)
            try:
                sz_kb = os.path.getsize(fp) / 1024
                color = CP_RED if sz_kb > 500 else CP_YELLOW if sz_kb > 250 else CP_TEXT
            except Exception:
                color = CP_TEXT
            lbl.setStyleSheet(f"color: {color}; background: transparent; font-size: {SOURCE_FILES_FONT_SIZE}pt;")
            mode_combo.setEnabled(True)
            self.status_cb(f"Enabled: {os.path.basename(fp)}")
        else:
            self.disabled_files.add(fp)
            self._apply_toggle_style(btn, False)
            lbl.setStyleSheet(f"color: {CP_SUB}; background: transparent; font-size: {SOURCE_FILES_FONT_SIZE}pt; text-decoration: line-through;")
            mode_combo.setEnabled(False)
            self.status_cb(f"Disabled: {os.path.basename(fp)}")
        self._save_session()

    def _file_item_context_menu(self, fp: str, item: QListWidgetItem, pos, widget: QWidget):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT};
                font-family: 'Consolas'; font-size: 9pt;
            }}
            QMenu::item:selected {{ background-color: #1a3a3a; color: {CP_CYAN}; }}
        """)
        act_remove = menu.addAction(f"✕  Remove  {os.path.basename(fp)}")
        action = menu.exec(widget.mapToGlobal(pos))
        if action == act_remove:
            self._remove_file(fp, item)

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

    # ── Header bar actions ────────────────────────────────────────────────────

    def _sort_by_ext(self):
        if self._sort_mode == "ext":
            self._sort_mode = "ext_rev"
        elif self._sort_mode == "ext_rev":
            self._sort_mode = "none"
        else:
            self._sort_mode = "ext"
        self._apply_sort()
        self._update_sort_buttons()

    def _sort_by_name(self):
        if self._sort_mode == "name":
            self._sort_mode = "name_rev"
        elif self._sort_mode == "name_rev":
            self._sort_mode = "none"
        else:
            self._sort_mode = "name"
        self._apply_sort()
        self._update_sort_buttons()

    def _sort_by_tokens(self):
        if self._sort_mode == "tokens":
            self._sort_mode = "tokens_rev"
        elif self._sort_mode == "tokens_rev":
            self._sort_mode = "none"
        else:
            self._sort_mode = "tokens"
        self._apply_sort()
        self._update_sort_buttons()

    def _toggle_all(self):
        # If any file is enabled → disable all. If all disabled → enable all.
        if len(self.disabled_files) < len(self.files):
            self.disabled_files = set(self.files)
            self.status_cb("All files disabled")
        else:
            self.disabled_files.clear()
            self.status_cb("All files enabled")
        self._refresh_file_items()
        self._save_session()

    def _apply_sort(self):
        """Re-order self.files according to current _sort_mode, then refresh."""
        enabled  = [fp for fp in self.files if fp not in self.disabled_files]
        disabled = [fp for fp in self.files if fp in self.disabled_files]

        def sort_key(fp):
            if self._sort_mode in ("ext", "ext_rev"):
                return os.path.splitext(fp)[1].lower()
            elif self._sort_mode in ("tokens", "tokens_rev"):
                try:
                    return os.path.getsize(fp)
                except Exception:
                    return 0
            else:  # name / name_rev
                return os.path.basename(fp).lower()

        reverse = self._sort_mode in ("ext_rev", "name_rev", "tokens_rev")

        if self._sort_mode != "none":
            enabled.sort(key=sort_key, reverse=reverse)
            disabled.sort(key=sort_key, reverse=reverse)

        self.files = enabled + disabled
        self._refresh_file_items()

    def _update_sort_buttons(self):
        dim    = f"color: {CP_SUB};"
        active = f"color: {CP_CYAN}; text-decoration: underline;"
        base   = "background: transparent; border: none; font-family: 'Consolas'; font-size: 8pt; font-weight: bold; padding: 0 2px;"

        ext_s    = active if self._sort_mode in ("ext",    "ext_rev")    else dim
        name_s   = active if self._sort_mode in ("name",   "name_rev")   else dim
        tokens_s = active if self._sort_mode in ("tokens", "tokens_rev") else dim

        ext_arrow    = "↑" if self._sort_mode == "ext_rev"    else "↓" if self._sort_mode == "ext"    else "↕"
        name_arrow   = "↑" if self._sort_mode == "name_rev"   else "↓" if self._sort_mode == "name"   else "↕"
        tokens_arrow = "↑" if self._sort_mode == "tokens_rev" else "↓" if self._sort_mode == "tokens" else "↕"

        self.btn_col_ext.setText(f"EXT {ext_arrow}")
        self.btn_col_ext.setStyleSheet(f"QPushButton {{ {base} {ext_s} }} QPushButton:hover {{ color: {CP_CYAN}; }}")
        self.btn_col_name.setText(f"NAME {name_arrow}")
        self.btn_col_name.setStyleSheet(f"QPushButton {{ {base} {name_s} }} QPushButton:hover {{ color: {CP_CYAN}; }}")
        self.btn_col_tokens.setText(f"TOK {tokens_arrow}")
        self.btn_col_tokens.setStyleSheet(f"QPushButton {{ {base} {tokens_s} }} QPushButton:hover {{ color: {CP_CYAN}; }}")

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── PROJECTS SIDEBAR ─────────────────────────────────────
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 6, 0)
        sidebar_layout.setSpacing(8)

        grp_projects = QGroupBox("PROJECTS")
        vp = QVBoxLayout(grp_projects)

        self.project_search = QLineEdit()
        self.project_search.setPlaceholderText("🔍 Search projects…")
        self.project_search.textChanged.connect(self._filter_projects)
        vp.addWidget(self.project_search)

        self.project_list = QListWidget()
        self.project_list.setObjectName("project_list_widget")
        self.project_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.project_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM};
                outline: none;
            }}
            QListWidget::item {{
                background: transparent;
                border: none;
                border-bottom: 1px solid #1a1a1a;
            }}
            QListWidget::item:selected, QListWidget::item:hover {{
                background: transparent;
                border: none;
                outline: none;
            }}
        """)
        self.project_list.itemClicked.connect(self._on_project_clicked)
        self.project_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.project_list.customContextMenuRequested.connect(self._project_context_menu)
        vp.addWidget(self.project_list)

        sidebar_layout.addWidget(grp_projects)
        
        btn_row_side = QHBoxLayout()
        btn_add_dir = QPushButton("📁 NEW ROOT")
        btn_add_dir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_dir.clicked.connect(self._add_dir)
        btn_row_side.addWidget(btn_add_dir)
        sidebar_layout.addLayout(btn_row_side)

        # ── MIDDLE PANEL (FILES) ─────────────────────────────────
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 6, 0)
        left_layout.setSpacing(8)

        grp_files = QGroupBox("SOURCE FILES")
        vf = QVBoxLayout(grp_files)

        # Path Label + Top Action Buttons Row (Clear & Toggle All)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(4)

        self.project_path_lbl = QLabel("<not set>")
        self.project_path_lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.project_path_lbl.setStyleSheet(
            "color: lightgreen; font-size: 9pt; font-family: 'Consolas';"
        )
        self.project_path_lbl.setWordWrap(False)
        self.project_path_lbl.setToolTip("Choose a directory to use as the project root")

        btn_open_folder = QPushButton("📂")
        btn_open_folder.setFixedHeight(22)
        btn_open_folder.setFixedWidth(28)
        btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open_folder.setToolTip("Open active project root folder in File Manager")
        btn_open_folder.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_YELLOW};
                font-size: 9pt; padding: 2px;
            }}
            QPushButton:hover {{ border-color: {CP_YELLOW}; background-color: #2a2a2a; }}
        """)
        btn_open_folder.clicked.connect(self._open_project_folder)

        btn_clear = QPushButton("✕ CLEAR")
        btn_clear.setFixedHeight(22)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT};
                font-size: 8pt; padding: 2px 6px; font-weight: bold;
            }}
            QPushButton:hover {{ border-color: {CP_RED}; color: {CP_RED}; }}
        """)
        btn_clear.clicked.connect(self._clear_files)

        btn_all_en = QPushButton("⬤ ALL")
        btn_all_en.setFixedHeight(22)
        btn_all_en.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_all_en.setToolTip("Toggle all files enabled/disabled")
        btn_all_en.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT};
                font-size: 8pt; padding: 2px 6px; font-weight: bold;
            }}
            QPushButton:hover {{ border-color: {CP_GREEN}; color: {CP_GREEN}; }}
        """)
        btn_all_en.clicked.connect(self._toggle_all)

        top_bar.addWidget(self.project_path_lbl, 1)
        top_bar.addWidget(btn_open_folder, 0)
        top_bar.addWidget(btn_clear, 0)
        top_bar.addWidget(btn_all_en, 0)

        vf.addLayout(top_bar)

        # File List Search/Filter Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter files by name…")
        self.search_input.textChanged.connect(self._filter_files)
        vf.addWidget(self.search_input)

        # Bulk actions row (shown/hidden via Settings → Show File Mode Controls)
        self.file_mode_bar = QWidget()
        self.file_mode_bar.setStyleSheet("background: transparent;")
        bulk_row = QHBoxLayout(self.file_mode_bar)
        bulk_row.setContentsMargins(0, 0, 0, 0)
        bulk_row.setSpacing(4)
        
        self.chk_minify = QCheckBox("Minify")
        self.chk_minify.setChecked(False)
        self.chk_minify.setToolTip("Strips comments and blank lines to save tokens.")
        self.chk_minify.stateChanged.connect(self._save_session)
        bulk_row.addWidget(self.chk_minify)
        
        bulk_row.addStretch()
        
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
        self.file_mode_bar.setVisible(SHOW_FILE_MODE_CONTROLS)
        vf.addWidget(self.file_mode_bar)

        # ── Column header bar ──────────────────────────────────
        header_bar = QWidget()
        header_bar.setStyleSheet(f"background: {CP_PANEL}; border: 1px solid {CP_DIM};")
        header_bar.setFixedHeight(22)
        hh = QHBoxLayout(header_bar)
        hh.setContentsMargins(4, 0, 4, 0)
        hh.setSpacing(2)

        self.btn_col_ext = QPushButton("EXT ↕")
        self.btn_col_ext.setFixedHeight(20)
        self.btn_col_ext.setMinimumWidth(38)
        self.btn_col_ext.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_col_ext.setToolTip("Sort by file extension")
        self.btn_col_ext.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {CP_SUB}; font-family: 'Consolas'; font-size: 7.5pt; font-weight: bold;
                padding: 0 1px;
            }}
            QPushButton:hover {{ color: {CP_CYAN}; }}
        """)
        self.btn_col_ext.clicked.connect(self._sort_by_ext)

        self.btn_col_name = QPushButton("NAME ↕")
        self.btn_col_name.setFixedHeight(20)
        self.btn_col_name.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_col_name.setToolTip("Sort by file name")
        self.btn_col_name.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {CP_SUB}; font-family: 'Consolas'; font-size: 7.5pt; font-weight: bold;
                padding: 0 1px;
            }}
            QPushButton:hover {{ color: {CP_CYAN}; }}
        """)
        self.btn_col_name.clicked.connect(self._sort_by_name)

        self.btn_col_tokens = QPushButton("TOK ↕")
        self.btn_col_tokens.setFixedHeight(20)
        self.btn_col_tokens.setMinimumWidth(42)
        self.btn_col_tokens.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_col_tokens.setToolTip("Sort by estimated token count")
        self.btn_col_tokens.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {CP_SUB}; font-family: 'Consolas'; font-size: 7.5pt; font-weight: bold;
                padding: 0 1px;
            }}
            QPushButton:hover {{ color: {CP_CYAN}; }}
        """)
        self.btn_col_tokens.clicked.connect(self._sort_by_tokens)

        hh.addWidget(self.btn_col_ext)
        hh.addWidget(self.btn_col_name, 1)
        hh.addWidget(self.btn_col_tokens)
        vf.addWidget(header_bar)
        # ── end header bar ─────────────────────────────────────

        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.file_list.viewport().installEventFilter(self)
        vf.addWidget(self.file_list)
        left_layout.addWidget(grp_files, 1)

        # ── RIGHT PANEL (PROMPT) ─────────────────────────────────

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
        self.splitter = splitter
        self.splitter.addWidget(sidebar_widget)
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 2)
        self.apply_panel_sizes()

        layout.addWidget(self.splitter)

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
        self._populate_projects()


    def _load_dir(self, d: str, selected_exts: set[str] = None, overwrite_recent: bool = False):
        d = os.path.normpath(d)
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
                fp = os.path.normpath(os.path.join(root, fn))
                added_files.append(fp)
                if fp not in self.files:
                    self.files.append(fp)
                    self._add_file_item(fp)
                    count += 1
        
        exts_list = list(selected_exts) if selected_exts is not None else list(discovered_exts)
        self._set_project_root(d, save_recent=False)
        add_recent(d, added_files, exts_list, overwrite_existing=overwrite_recent)
        self.status_cb(f"Added {count} file(s) from directory")
        self._update_root()
        self._save_session()

    def _load_specific_files(self, d: str, files: list[str], extensions: list[str], disabled_files: list[str] = None):
        if self.project_root:
            self._sync_to_recent_projects()

        if not files:
            self._load_all_project_files(d)
            return

        self.files.clear()
        self.file_list.clear()
        self.disabled_files = {os.path.normpath(f) for f in disabled_files} if disabled_files is not None else set()
        
        count = 0
        for fp in files:
            norm_fp = os.path.normpath(fp)
            if os.path.exists(norm_fp):
                self.files.append(norm_fp)
                self._add_file_item(norm_fp)
                count += 1
                
        self._set_project_root(d, save_recent=False)
        add_recent(d, self.files, extensions, overwrite_existing=False, disabled_files=list(self.disabled_files))
        self.status_cb(f"Loaded {count} saved file(s) for project: {os.path.basename(d)}")
        self._update_root()
        self._save_session()

    def _load_all_project_files(self, d: str):
        d = os.path.normpath(d)

        # Retrieve saved disabled files for target project d
        if os.path.normpath(self.project_root) == d:
            target_disabled = {f for f in self.disabled_files if is_subpath(f, d)}
        else:
            target_disabled = set()
            for item in load_recent_details():
                if os.path.normpath(item["path"]) == d:
                    target_disabled = {os.path.normpath(f) for f in item.get("disabled_files", []) if is_subpath(f, d)}
                    break

        old_external = [f for f in self.files if not is_subpath(f, d)]
        old_disabled_ext = [f for f in self.disabled_files if not is_subpath(f, d)]

        self.files.clear()
        self.file_list.clear()
        self.disabled_files = target_disabled
        
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
                    
        self._set_project_root(d, save_recent=False)
        add_recent(d, added_files, list(discovered_exts), overwrite_existing=True, disabled_files=list(self.disabled_files))

        total_removed = len(old_external) + len(old_disabled_ext)
        if total_removed > 0:
            self.status_cb(f"Re-scanned {count} file(s). Purged {total_removed} external file(s) outside project folder.")
        else:
            self.status_cb(f"Re-scanned and loaded {count} file(s) from directory")

        self._update_root()
        self._save_session()

    def _edit_project(self, path: str):
        norm_p = os.path.normpath(path)
        items = load_recent_details()
        target_item = None
        for item in items:
            if os.path.normpath(item["path"]) == norm_p:
                target_item = item
                break

        if not target_item:
            target_item = {"path": norm_p, "name": "", "category": "", "icon": "", "disabled_files": [], "pinned": False, "pin_index": 1}

        curr_disabled = target_item.get("disabled_files", [])
        if norm_p == os.path.normpath(self.project_root):
            curr_disabled = list(self.disabled_files)

        dlg = EditProjectDialog(
            path=norm_p,
            name=target_item.get("name", ""),
            category=target_item.get("category", ""),
            icon=target_item.get("icon", ""),
            disabled_files=curr_disabled,
            pinned=target_item.get("pinned", False),
            pin_index=target_item.get("pin_index", 1),
            parent=self
        )

        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_name, new_cat, new_icon, updated_disabled, new_pinned, new_pin_index = dlg.get_details()
            norm_p = os.path.normpath(path)
            
            for item in items:
                if os.path.normpath(item["path"]) == norm_p:
                    item["name"] = new_name
                    item["category"] = new_cat
                    item["icon"] = new_icon
                    item["disabled_files"] = updated_disabled

            PROJECT_ICONS[norm_p] = new_icon

            # Automatically shift existing items and re-sequence pin indices cleanly
            resequence_pinned_projects(items, target_path=norm_p, set_pinned=new_pinned, target_index=new_pin_index)

            save_recent(items)

            if norm_p == os.path.normpath(self.project_root):
                self.disabled_files = set(updated_disabled)
                self._refresh_file_items()

            self.status_cb(f"Updated details for project: {os.path.basename(path)}")
            self._populate_projects()




    def _clear_files(self):
        self.files.clear()
        self.file_list.clear()
        self._save_session()
        self.status_cb("File list cleared")

    def _open_project_folder(self):
        root = self.project_root.strip()
        if root and os.path.exists(root):
            self._open_explorer(root)
            self.status_cb(f"Opened project directory: {root}")
        else:
            self.status_cb("⚠ No valid project directory set")


    def _populate_projects(self):
        self.project_list.clear()
        items = load_recent_details()
        items = resequence_pinned_projects(items)

        # Sort pinned projects to top by pin_index ascending, then unpinned projects
        def sort_projects_key(item):
            is_pinned = item.get("pinned", False)
            pin_idx = item.get("pin_index", 0)
            return (0 if is_pinned else 1, pin_idx if is_pinned else 0)

        items.sort(key=sort_projects_key)

        for item in items:
            path = item["path"]
            name = item.get("name")
            files = item.get("files", [])
            is_pinned = item.get("pinned", False)
            pin_idx = item.get("pin_index", 0)

            li = QListWidgetItem()
            li.setData(Qt.ItemDataRole.UserRole, item)

            widget = QWidget()
            widget.setObjectName("proj_item_container")
            vl = QVBoxLayout(widget)
            vl.setContentsMargins(10, 4, 6, 4)
            vl.setSpacing(2)
            vl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

            category = item.get("category", "")
            icon_val = item.get("icon", "") or PROJECT_ICONS.get(os.path.normpath(path), "")

            display_name = name if name else os.path.basename(path)
            if not display_name: display_name = path

            lbl_name = QLabel(display_name)
            lbl_name.setObjectName("proj_name_label")
            lbl_name.setStyleSheet(f"color: {PROJECTS_NAME_COLOR}; font-weight: bold; font-size: {PROJECTS_FONT_SIZE}pt;")

            hl_title = QHBoxLayout()
            hl_title.setContentsMargins(0, 0, 0, 0)
            hl_title.setSpacing(6)

            if icon_val:
                icon_lbl = QLabel()
                icon_lbl.setPixmap(render_extension_icon(icon_val, EXTENSION_ICON_SIZE))
                icon_lbl.setFixedSize(EXTENSION_ICON_SIZE, EXTENSION_ICON_SIZE)
                icon_lbl.setStyleSheet("background: transparent;")
                hl_title.addWidget(icon_lbl, 0)

            hl_title.addWidget(lbl_name, 0)

            if is_pinned:
                red_dot = QLabel("🔴")
                red_dot.setStyleSheet(f"font-size: 7.5pt; color: {CP_RED}; background: transparent;")
                red_dot.setToolTip(f"Pinned Project (Index #{pin_idx})")
                hl_title.addWidget(red_dot, 0)

            hl_title.addStretch(1)

            if category:
                lbl_cat = QLabel(f"[{category}]")
                lbl_cat.setStyleSheet(f"color: {CP_CYAN}; font-size: 8pt; font-weight: bold;")
                hl_title.addWidget(lbl_cat, 0)

            vl.addLayout(hl_title)

            lbl_path = QLabel(path)
            lbl_path.setObjectName("proj_path_label")
            lbl_path.setStyleSheet(f"color: {CP_SUB}; font-size: 7.5pt;")

            if SHOW_PROJECT_PATHS:
                vl.addWidget(lbl_path)

            item_h = max(44, PROJECTS_FONT_SIZE + 28)
            li.setSizeHint(QSize(0, item_h))
            self.project_list.addItem(li)
            self.project_list.setItemWidget(li, widget)

        self._filter_projects()
        self._update_active_project_highlight()

    def _filter_projects(self):
        query = self.project_search.text().strip().lower()
        for i in range(self.project_list.count()):
            item = self.project_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            path = data.get("path", "").lower()
            name = data.get("name", "").lower()
            category = data.get("category", "").lower()
            visible = (not query) or (query in path) or (query in name) or (query in category)
            item.setHidden(not visible)

    def _update_active_project_highlight(self):
        norm_root = os.path.normpath(self.project_root).lower() if self.project_root else ""
        for i in range(self.project_list.count()):
            item = self.project_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if not data:
                continue
            path = os.path.normpath(data.get("path", "")).lower()
            widget = self.project_list.itemWidget(item)
            if not widget:
                continue
            
            is_active = (norm_root and path == norm_root)
            
            lbl_name = widget.findChild(QLabel, "proj_name_label")
            lbl_path = widget.findChild(QLabel, "proj_path_label")
            
            if is_active:
                widget.setStyleSheet(f"""
                    QWidget#proj_item_container {{
                        background-color: #1c3335;
                        border-left: 3px solid {CP_CYAN};
                    }}
                    QLabel {{
                        border: none;
                        background: transparent;
                    }}
                """)
            else:
                widget.setStyleSheet("""
                    QWidget#proj_item_container {
                        background-color: transparent;
                        border-left: 3px solid transparent;
                    }
                    QLabel {
                        border: none;
                        background: transparent;
                    }
                """)

            if lbl_name:
                lbl_name.setStyleSheet(f"color: {PROJECTS_NAME_COLOR}; font-weight: bold; font-size: {PROJECTS_FONT_SIZE}pt;")
            if lbl_path:
                lbl_path.setStyleSheet(f"color: {CP_SUB}; font-size: 7.5pt;")


    def _on_project_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        path = data.get("path")
        if not path:
            return

        norm_p = os.path.normpath(path)
        # Fetch fresh details from disk to avoid stale QListWidgetItem data
        fresh_items = load_recent_details()
        fresh_target = None
        for fi in fresh_items:
            if os.path.normpath(fi["path"]) == norm_p:
                fresh_target = fi
                break

        files = fresh_target.get("files", []) if fresh_target else data.get("files", [])
        extensions = fresh_target.get("extensions", []) if fresh_target else data.get("extensions", [])
        disabled_files = fresh_target.get("disabled_files", []) if fresh_target else data.get("disabled_files", [])

        self._load_specific_files(path, files, extensions, disabled_files)

    def _project_context_menu(self, pos):
        item = self.project_list.itemAt(pos)
        if not item: return
        data = item.data(Qt.ItemDataRole.UserRole)
        path = data.get("path")
        name = data.get("name") or os.path.basename(path) or path
        is_pinned = data.get("pinned", False)
        pin_index = data.get("pin_index", 1)

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT}; }}
            QMenu::item:selected {{ background-color: #1a3a3a; color: {CP_CYAN}; }}
        """)

        if is_pinned:
            act_pin = menu.addAction(f"📌  Unpin Project (Index #{pin_index})")
        else:
            act_pin = menu.addAction("📌  Pin Project to Top...")

        act_load_all = menu.addAction("🔄  Re-scan & Load All")
        act_edit     = menu.addAction("✏️  Edit Project Details")
        act_open     = menu.addAction("📂  Open in Explorer")
        menu.addSeparator()
        act_remove   = menu.addAction("✕  Remove from List")

        action = menu.exec(self.project_list.viewport().mapToGlobal(pos))
        if action == act_pin:
            items = load_recent_details()
            norm_p = os.path.normpath(path)
            if is_pinned:
                resequence_pinned_projects(items, target_path=norm_p, set_pinned=False)
                self.status_cb(f"Unpinned project: {name}")
            else:
                val, ok = QInputDialog.getInt(
                    self, "Pin Project",
                    f"Enter pin index for '{name}' (1 = top position):",
                    value=1, min=1, max=999
                )
                if ok:
                    resequence_pinned_projects(items, target_path=norm_p, set_pinned=True, target_index=val)
                    self.status_cb(f"Pinned '{name}' at index #{val}")

            save_recent(items)
            self._populate_projects()
        elif action == act_load_all:
            self._load_all_project_files(path)
            self._populate_projects()
        elif action == act_edit:
            self._edit_project(path)
        elif action == act_open:
            self._open_explorer(path)
        elif action == act_remove:
            norm_p = os.path.normpath(path).lower()
            if self.project_root and os.path.normpath(self.project_root).lower() == norm_p:
                self.project_root = ""
                self.files.clear()
                self.disabled_files.clear()
                self.file_list.clear()
                self._update_project_label()
            remove_recent(path)
            self._save_session()
            self._populate_projects()
            self.status_cb(f"Removed project: {path}")

    def _open_explorer(self, p):
        try:
            if hasattr(os, 'startfile'):
                os.startfile(p)
            elif sys.platform.startswith('darwin'):
                import subprocess
                subprocess.Popen(['open', p])
            else:
                import subprocess
                subprocess.Popen(['xdg-open', p])
        except Exception:
            pass


    def _generate(self):
        if not self.files and not self.project_root:
            self.status_cb("⚠ Add files or choose a directory first")
            return

        prompt = self._build_prompt()
        if not prompt:
            self.status_cb("⚠ Nothing to generate")
            return

        self.prompt_out.setPlainText(prompt)

        # Save prompt to external MD file for history/external use
        try:
            output_md = r"C:\@delta\output\code_merger\code_merger_generated_prmpt.md"
            os.makedirs(os.path.dirname(output_md), exist_ok=True)
            with open(output_md, 'w', encoding='utf-8') as f:
                f.write(prompt)
        except Exception as e:
            print(f"Error auto-saving prompt to {output_md}: {e}", file=sys.stderr)

        if self.files:
            self.status_cb("Prompt generated — saved to disk & ready to copy")
        else:
            self.status_cb("New project prompt generated — saved to disk & ready to copy")

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


# ── DIFF PREVIEW DIALOG ───────────────────────────────────────────────────────
class DiffPreviewDialog(QDialog):
    """Interactive visual diff preview dialog allowing selective block merge."""
    def __init__(self, changes: list[dict], root: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DIFF PREVIEW & SELECTIVE MERGE")
        self.resize(1180, 820)
        self.setStyleSheet(THEME)
        self.changes = list(changes)
        self.root = root
        self.check_states: list[QCheckBox] = []
        self.diff_views: list[QTextEdit] = []
        self.groups: list[QGroupBox] = []
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Header bar with summary & view toggles
        top_bar = QHBoxLayout()
        self.lbl_hdr = QLabel(f"Review changes ({len(self.changes)} block(s) detected):")
        self.lbl_hdr.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 11pt;")
        top_bar.addWidget(self.lbl_hdr, 1)

        btn_exp_all = QPushButton("📖 EXPAND ALL")
        btn_coll_all = QPushButton("📁 COLLAPSE ALL")
        btn_exp_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_coll_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exp_all.setStyleSheet(f"background-color: {CP_DIM}; padding: 4px 8px; font-size: 8.5pt;")
        btn_coll_all.setStyleSheet(f"background-color: {CP_DIM}; padding: 4px 8px; font-size: 8.5pt;")
        btn_exp_all.clicked.connect(self._expand_all)
        btn_coll_all.clicked.connect(self._collapse_all)

        top_bar.addWidget(btn_exp_all)
        top_bar.addWidget(btn_coll_all)
        layout.addLayout(top_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        v_box = QVBoxLayout(scroll_content)
        v_box.setSpacing(14)
        v_box.setAlignment(Qt.AlignmentFlag.AlignTop)

        import difflib

        for idx, ch in enumerate(self.changes):
            fpath = os.path.join(self.root, ch["file"].lstrip("/\\"))
            mode = ch["mode"]

            group = QGroupBox(f" Block #{idx+1} · [{mode.upper()}]  {ch['file']} ")
            g_layout = QVBoxLayout(group)
            g_layout.setSpacing(6)
            g_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            chk_row = QHBoxLayout()
            chk = QCheckBox("Apply this change block")
            chk.setChecked(True)
            chk.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold; font-size: 9.5pt;")
            self.check_states.append(chk)
            chk_row.addWidget(chk, 1)

            btn_toggle_view = QPushButton("▲ Minimize")
            btn_toggle_view.setFixedWidth(90)
            btn_toggle_view.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_toggle_view.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; font-size: 8pt; color: {CP_SUB};")
            chk_row.addWidget(btn_toggle_view)
            g_layout.addLayout(chk_row)

            diff_view = QTextEdit()
            diff_view.setReadOnly(True)
            diff_view.setFont(QFont("Consolas", 10))
            diff_view.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
            diff_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            diff_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            diff_view.setStyleSheet(f"background-color: #060606; border: 1px solid {CP_DIM}; padding: 6px;")
            self.diff_views.append(diff_view)

            old_lines = []
            new_lines = []

            if os.path.exists(fpath):
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        old_lines = f.read().replace('\r\n', '\n').splitlines()
                except Exception:
                    pass

            if mode == "replace_file":
                new_lines = ch["to"].replace('\r\n', '\n').splitlines()
            elif mode == "replace_block":
                from_lines = ch["from"].replace('\r\n', '\n').splitlines()
                to_lines = ch["to"].replace('\r\n', '\n').splitlines()
                old_lines = from_lines
                new_lines = to_lines
            elif mode == "insert_after":
                old_lines = ch["after"].replace('\r\n', '\n').splitlines()
                new_lines = old_lines + ch["insert"].replace('\r\n', '\n').splitlines()
            elif mode == "delete_block":
                old_lines = ch["from"].replace('\r\n', '\n').splitlines()
                new_lines = []

            diff = difflib.unified_diff(
                old_lines, new_lines,
                fromfile="Original", tofile="Proposed Change", lineterm=""
            )
            diff_lines = list(diff)[2:]  # Skip header

            html_parts = []
            for line in diff_lines:
                escaped = (line.replace("&", "&amp;")
                               .replace("<", "&lt;")
                               .replace(">", "&gt;"))
                if line.startswith('+'):
                    html_parts.append(f'<div style="color: {CP_GREEN}; background-color: #002e07; font-weight: bold; padding: 1px 4px; white-space: pre-wrap; word-wrap: break-word;">{escaped}</div>')
                elif line.startswith('-'):
                    html_parts.append(f'<div style="color: {CP_RED}; background-color: #3b000d; padding: 1px 4px; white-space: pre-wrap; word-wrap: break-word;">{escaped}</div>')
                elif line.startswith('@@'):
                    html_parts.append(f'<div style="color: {CP_CYAN}; font-weight: bold; background-color: #11222e; margin-top: 4px; margin-bottom: 4px; padding: 2px 4px; white-space: pre-wrap; word-wrap: break-word;">{escaped}</div>')
                else:
                    html_parts.append(f'<div style="color: {CP_TEXT}; padding: 0 4px; white-space: pre-wrap; word-wrap: break-word;">{escaped}</div>')

            diff_view.setHtml("<div style='margin:0; font-family:Consolas; line-height:1.3; white-space: pre-wrap; word-wrap: break-word;'>" + "".join(html_parts) + "</div>")

            # Expand box to full content height so inner scrollbars are completely eliminated
            diff_view.document().adjustSize()
            full_content_height = max(100, int(diff_view.document().size().height()) + 24)
            diff_view.setFixedHeight(full_content_height)

            btn_toggle_view.clicked.connect(lambda _, dv=diff_view, btn=btn_toggle_view: self._toggle_single_view(dv, btn))

            g_layout.addWidget(diff_view)
            self.groups.append(group)
            v_box.addWidget(group)

        v_box.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Bottom Selection & Action Buttons
        btn_row = QHBoxLayout()
        btn_all = QPushButton("SELECT ALL")
        btn_none = QPushButton("SELECT NONE")
        btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_none.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_all.clicked.connect(lambda: [c.setChecked(True) for c in self.check_states])
        btn_none.clicked.connect(lambda: [c.setChecked(False) for c in self.check_states])

        btn_ok = QPushButton("✔ APPLY SELECTED CHANGES")
        btn_cancel = QPushButton("✕ CLOSE")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setStyleSheet(f"QPushButton {{ border-color: {CP_GREEN}; color: {CP_GREEN}; font-size: 10pt; }}"
                             f"QPushButton:hover {{ background: {CP_GREEN}; color: #000; border-color: {CP_GREEN}; }}")
        btn_cancel.setStyleSheet(f"QPushButton {{ border-color: {CP_RED}; color: {CP_RED}; font-size: 10pt; }}"
                                 f"QPushButton:hover {{ background: {CP_RED}; color: #000; border-color: {CP_RED}; }}")

        btn_ok.clicked.connect(self._on_apply_selected)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(btn_all)
        btn_row.addWidget(btn_none)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

    def _on_apply_selected(self):
        selected_indices = [i for i, chk in enumerate(self.check_states) if chk.isChecked()]
        if not selected_indices:
            QMessageBox.information(self, "No Selection", "Please select at least one change block to apply.")
            return

        selected_changes = [self.changes[i] for i in selected_indices]
        backup = self.parent().chk_backup.isChecked() if hasattr(self.parent(), 'chk_backup') else True
        match_mode = "fuzzy" if hasattr(self.parent(), 'match_mode_cb') and self.parent().match_mode_cb and "Fuzzy" in self.parent().match_mode_cb() else "exact"

        results = apply_changes(selected_changes, self.root, backup, match_mode=match_mode)

        failed_indices = []
        successful_indices = []

        for idx_in_sel, res in enumerate(results):
            orig_idx = selected_indices[idx_in_sel]
            if res.startswith("✔"):
                successful_indices.append(orig_idx)
            else:
                failed_indices.append((orig_idx, res))

        if hasattr(self.parent(), 'result_out'):
            self.parent().result_out.setPlainText("\n\n".join(results))

        # Remove UI cards for successful merges
        for orig_idx in sorted(successful_indices, reverse=True):
            group_widget = self.groups[orig_idx]
            group_widget.setParent(None)
            del self.changes[orig_idx]
            del self.check_states[orig_idx]
            del self.diff_views[orig_idx]
            del self.groups[orig_idx]

        if not self.changes:
            if hasattr(self.parent(), 'status_cb'):
                self.parent().status_cb(f"✔ All {len(successful_indices)} change block(s) merged successfully!")
            self.accept()
        elif failed_indices:
            if hasattr(self.parent(), 'status_cb'):
                self.parent().status_cb(f"⚠ {len(failed_indices)} change(s) failed. Showing failed block(s) for review.")
            self.lbl_hdr.setText(f"⚠ {len(self.changes)} change block(s) remaining (Failed to merge):")
            self.lbl_hdr.setStyleSheet(f"color: {CP_RED}; font-weight: bold; font-size: 11pt;")

    def _toggle_single_view(self, diff_view: QTextEdit, btn: QPushButton):
        if diff_view.isVisible():
            diff_view.setVisible(False)
            btn.setText("▼ Expand")
        else:
            diff_view.setVisible(True)
            btn.setText("▲ Minimize")

    def _expand_all(self):
        for dv in self.diff_views:
            dv.setVisible(True)

    def _collapse_all(self):
        for dv in self.diff_views:
            dv.setVisible(False)

    def get_selected_changes(self) -> list[dict]:
        return [ch for ch, chk in zip(self.changes, self.check_states) if chk.isChecked()]



# ── MERGE TAB ─────────────────────────────────────────────────────────────────
class MergeTab(QWidget):
    def __init__(self, status_cb, match_mode_cb=None):
        super().__init__()
        self.status_cb = status_cb
        self.match_mode_cb = match_mode_cb
        self._parsed_commit_msg = ""
        self._build()
        self._load_prefs()

    def _save_prefs(self):
        import json
        try:
            data = {}
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
        except Exception:
            data = {}
        data['backup']  = self.chk_backup.isChecked()
        data['preview'] = self.chk_preview.isChecked()
        try:
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving prefs: {e}", file=sys.stderr)

    def _load_prefs(self):
        import json
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
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

        # Silently keep root_input for internal path resolution
        self.root_input = QLineEdit()

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
            self._parse()
        if not self._pending_changes:
            self.status_cb("⚠ Parse changes first")
            return
        root = self.root_input.text().strip()
        if not root or not os.path.isdir(root):
            self.status_cb("⚠ Set a valid project root directory")
            return

        if self.chk_preview.isChecked():
            dlg = DiffPreviewDialog(self._pending_changes, root, self)
            dlg.exec()
        else:
            match_mode = "fuzzy" if self.match_mode_cb and self.match_mode_cb() and "Fuzzy" in self.match_mode_cb() else "exact"
            results = apply_changes(self._pending_changes, root, self.chk_backup.isChecked(), match_mode=match_mode)
            ok  = sum(1 for r in results if r.startswith("✔"))
            err = len(results) - ok

            if ok > 0:
                commit_msg = self._parsed_commit_msg or "update files"
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

    def _preview_diff(self):
        if not self._pending_changes:
            self._parse()
        if not self._pending_changes:
            return
        root = self.root_input.text().strip()
        if not root or not os.path.isdir(root):
            self.status_cb("⚠ Set a valid project root directory")
            return

        dlg = DiffPreviewDialog(self._pending_changes, root, self)
        dlg.exec()


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

    def _run_cmd(self):
        self.output_text.clear()
        self.status_cb("Running command…")
        
        d = self.get_root_fn()
        if not d or not os.path.isdir(d):
            self.status_cb("⚠ Invalid project root directory")
            self.output_text.setPlainText("Error: Invalid project root directory. Please load a project in the Prep tab.")
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
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 800)
        self.setMinimumSize(1024, 600)
        self.setStyleSheet(THEME)
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 4)
        root_layout.setSpacing(6)

        # Header
        self.hdr_lbl = QLabel(f"// {APP_NAME.upper()}")
        self.hdr_lbl.setStyleSheet(f"color: {CP_YELLOW}; font-size: 14pt; font-weight: bold; letter-spacing: 2px;")
        sub = QLabel("Prep files for AI  ·  Merge AI responses back to disk")
        sub.setStyleSheet(f"color: {CP_SUB}; font-size: 9pt;")
        root_layout.addWidget(self.hdr_lbl)
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

        self.combo_match_mode = QComboBox()
        self.combo_match_mode.addItems(["🎯 Exact Match", "⚡ Smart / Fuzzy Match"])
        self.combo_match_mode.setToolTip("Select code matching engine:\n• Exact Match: Strict string matching\n• Smart / Fuzzy Match: Insensitive to trailing spaces/minor LLM formatting errors")
        self.combo_match_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.combo_match_mode.setStyleSheet(f"""
            QComboBox {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 4px 8px;
                font-family: 'Consolas';
                font-size: 9pt;
                font-weight: bold;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                selection-background-color: {CP_CYAN};
                selection-color: black;
                border: 1px solid {CP_DIM};
            }}
        """)
        self._load_match_mode_pref()
        self.combo_match_mode.currentTextChanged.connect(self._save_match_mode_pref)

        corner_layout.addWidget(self.combo_match_mode)
        corner_layout.addWidget(btn_settings)
        corner_layout.addWidget(btn_restart)
        self.tabs.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)

        self.merge_tab = MergeTab(self._set_status, self.get_match_mode)
        self.prep_tab  = PrepTab(self._set_status, self.merge_tab.set_root)
        self.command_tab = CommandTab(self._set_status, lambda: self.merge_tab.root_input.text().strip())
        self.tabs.addTab(self.prep_tab,  "⚙  PREP  ( local → AI )")
        self.tabs.addTab(self.merge_tab, "⚡  MERGE  ( AI → local )")
        self.tabs.addTab(self.command_tab, "💻  COMMAND ( runner )")
        root_layout.addWidget(self.tabs)

    def _open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.setWindowTitle(APP_NAME)
            self.hdr_lbl.setText(f"// {APP_NAME.upper()}")
            self.prep_tab._refresh_file_items()
            self.prep_tab._populate_projects()
            self.prep_tab.file_mode_bar.setVisible(SHOW_FILE_MODE_CONTROLS)
            self.prep_tab.apply_panel_sizes()
            self._set_status(f"Settings saved. Updated GUI title to '{APP_NAME}'.")

    def get_match_mode(self) -> str:
        return self.combo_match_mode.currentText()

    def _load_match_mode_pref(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, dict) and 'match_mode' in data:
                    self.combo_match_mode.setCurrentText(data['match_mode'])
        except Exception:
            pass

    def _save_match_mode_pref(self, text: str):
        try:
            data = {}
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            if not isinstance(data, dict):
                data = {}
            data['match_mode'] = text
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


    def _set_status(self, msg: str):
        self.status_bar.showMessage(f"  {msg}")


if __name__ == "__main__":
    load_settings()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
