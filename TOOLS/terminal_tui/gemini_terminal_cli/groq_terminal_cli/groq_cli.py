#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import html
import json
import os
import platform
import re
import time
import subprocess
import sys
import textwrap
import unicodedata

import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Protocol.KDF import PBKDF2
    from Cryptodome.Random import get_random_bytes
except Exception:
    AES = None
    PBKDF2 = None
    get_random_bytes = None


DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_SYSTEM = (
    "You are a terminal coding assistant using Groq. "
    "Be concise, practical, and ask before making destructive changes. "
    "For code work, inspect with run_powershell commands first. "
    "Prefer fuzzy_apply_patch for edits."
)
DEFAULT_TOOL_LOOPS = 8
MAX_TEXT_CHARS = 12000
MODEL_PREFS_FILE = Path(__file__).with_name("model_prefs.json")
TOOLS_FILE = Path(__file__).with_name("tools.json")
PROMPT_HISTORY_FILE = Path(__file__).with_name("prompt_history.txt")
API_ACCOUNTS_FILE = Path(__file__).with_name("api_accounts.lock")
API_ACCOUNTS_MAGIC = b"GROQAPI1"
NOTIFICATION_FILE = Path(r"C:\Users\nahid\notification.txt")

try:
    import msvcrt
except Exception:
    msvcrt = None

try:
    from prompt_toolkit import prompt as pt_prompt
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.formatted_text import ANSI
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.shortcuts import CompleteStyle
    from prompt_toolkit.styles import Style
except Exception:
    pt_prompt = None
    AutoSuggestFromHistory = None
    Completer = None
    Completion = None
    ANSI = None
    InMemoryHistory = None
    CompleteStyle = None
    Style = None


def _now_stamp() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d-%H:%M")


def _now() -> dt.datetime:
    return dt.datetime.now()


def write_notification() -> None:
    try:
        NOTIFICATION_FILE.write_text(_now_stamp(), encoding="utf-8")
    except Exception:
        pass


def _ansi_wrap(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def info(text: str) -> None:
    print(_ansi_wrap(text, "36"))


def warn(text: str) -> None:
    print(_ansi_wrap(text, "33"))


def error(text: str) -> None:
    print(_ansi_wrap(text, "31"))
def _clean_response_text(text: str) -> str:
    """Removes <think>...</think> blocks from reasoning models."""
    if not text:
        return ""
    # Remove everything between <think> and </think> tags, including the tags themselves
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
def _visible_len(text: str) -> int:
    """Calculate the visible length of a string, ignoring ANSI escape codes and accounting for wide characters."""
    clean_text = re.sub(r'\x1b\[[0-9;]*[mK]', '', text)
    width = 0
    for char in clean_text:
        # unicodedata.east_asian_width returns 'W' (Wide) or 'F' (Fullwidth) for characters
        # that typically take up two columns in a terminal (like emojis or CJK characters).
        if unicodedata.east_asian_width(char) in ('W', 'F'):
            width += 2
        else:
            width += 1
    return width


def _format_seconds(seconds: float) -> str:
    total = max(0, int(seconds + 0.999))
    minutes, secs = divmod(total, 60)
    return f"{minutes:02d}:{secs:02d}"


def format_cooldown_until(until: Optional[dt.datetime]) -> str:
    if until is None:
        return ""
    remaining = int((until - _now()).total_seconds() + 0.999)
    if remaining <= 0:
        return ""
    return f"cooldown {_format_seconds(remaining)}"



def _render_inline_markdown(text: str) -> str:
    if not text:
        return text

    def replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        url = match.group(2)
        if sys.stdout.isatty():
            return f"{_ansi_wrap(label, '4;36')} ({url})"
        return f"{label} ({url})"

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, text)
    # Bold
    text = re.sub(r"(?<!\*)\*\*(.+?)\*\*(?!\*)", lambda m: _ansi_wrap(m.group(1), "1"), text)
    text = re.sub(r"(?<!_)__(.+?)__(?!_)", lambda m: _ansi_wrap(m.group(1), "1"), text)
    # Italic - more permissive boundary check to catch * at start of lines or inside punctuation
    text = re.sub(r"(\s|^|[(\[{])\*(?!\s)(.+?)(?<!\s)\*(\s|$|[.,!?;:)}\]])", lambda m: f"{m.group(1)}{_ansi_wrap(m.group(2), '3')}{m.group(3)}", text)
    text = re.sub(r"(\s|^|[(\[{])_(?!\s)(.+?)(?<!\s)_(\s|$|[.,!?;:)}\]])", lambda m: f"{m.group(1)}{_ansi_wrap(m.group(2), '3')}{m.group(3)}", text)
    # Inline Code
    text = re.sub(r"`([^`]+)`", lambda m: _ansi_wrap(m.group(1), "38;5;214"), text)
    return text


def _wrap_visible(text: str, max_width: int) -> List[str]:
    """Wraps text containing ANSI codes into multiple lines based on visible width."""
    if _visible_len(text) <= max_width:
        return [text]
    words = text.split(' ')
    lines = []
    cur_line = []
    cur_len = 0
    for word in words:
        w_len = _visible_len(word)
        if cur_len + w_len + (1 if cur_line else 0) <= max_width:
            cur_line.append(word)
            cur_len += w_len + (1 if cur_line else 0)
        else:
            if cur_line:
                lines.append(' '.join(cur_line))
            cur_line = [word]
            cur_len = w_len
    if cur_line:
        lines.append(' '.join(cur_line))
    return lines


def render_markdown_text(text: str) -> str:
    lines: List[str] = []
    in_code_block = False
    raw_lines = text.splitlines()
    idx = 0
    try:
        term_width = os.get_terminal_size().columns
    except Exception:
        term_width = 100

    while idx < len(raw_lines):
        line = raw_lines[idx]
        stripped_line = line.strip()
        
        # 1. Code Block Handling
        fence = re.match(r"^\s*```(\w+)?\s*$", line)
        if fence:
            in_code_block = not in_code_block
            lines.append(_ansi_wrap(line, "90"))
            idx += 1
            continue
        if in_code_block:
            lines.append(f"  {line}")
            idx += 1
            continue

        # 2. Table Handling
        if not in_code_block and "|" in stripped_line:
            table_rows = []
            while idx < len(raw_lines) and "|" in raw_lines[idx]:
                table_rows.append(raw_lines[idx])
                idx += 1
            
            if len(table_rows) >= 2:
                grid = []
                for row in table_rows:
                    row_content = row.strip()
                    if row_content.startswith("|"): row_content = row_content[1:]
                    if row_content.endswith("|"): row_content = row_content[:-1]
                    cells = [c.strip() for c in row_content.split("|")]
                    is_sep = all(set(c.replace(" ", "")) <= {"-", ":"} and "-" in c for c in cells)
                    rendered = [_render_inline_markdown(c) for c in cells] if not is_sep else []
                    grid.append({"rendered": rendered, "is_sep": is_sep})
                
                col_count = max(len(r["rendered"]) for r in grid if not r["is_sep"])
                col_widths = [0] * col_count
                for row in grid:
                    if row["is_sep"]: continue
                    for c_idx, cell in enumerate(row["rendered"]):
                        if c_idx < col_count:
                            col_widths[c_idx] = max(col_widths[c_idx], _visible_len(cell))
                
                total_w = sum(col_widths) + (col_count * 3) + 1
                if total_w > term_width:
                    shrink_factor = (term_width - 10) / total_w
                    col_widths = [max(10, int(w * shrink_factor)) for w in col_widths]

                border_color = "36"
                def get_sep_line(left, mid, right):
                    return _ansi_wrap(left + mid.join("─" * (w + 2) for w in col_widths) + right, border_color)

                lines.append(get_sep_line("┌", "┬", "┐"))
                v_bar = _ansi_wrap("│", border_color)

                for r_idx, row in enumerate(grid):
                    if row["is_sep"]:
                        lines.append(get_sep_line("├", "┼", "┤"))
                        continue
                    
                    wrapped_cells = []
                    for c_idx in range(col_count):
                        content = row["rendered"][c_idx] if c_idx < len(row["rendered"]) else ""
                        wrapped_cells.append(_wrap_visible(content, col_widths[c_idx]))
                    
                    row_height = max(len(c) for c in wrapped_cells)
                    
                    for sub_idx in range(row_height):
                        line_parts = []
                        for c_idx in range(col_count):
                            cell_lines = wrapped_cells[c_idx]
                            cell_line = cell_lines[sub_idx] if sub_idx < len(cell_lines) else ""
                            pad = " " * (col_widths[c_idx] - _visible_len(cell_line))
                            line_parts.append(f" {cell_line}{pad} ")
                        lines.append(f"{v_bar}{v_bar.join(line_parts)}{v_bar}")

                    if r_idx < len(grid) - 1 and not grid[r_idx+1]["is_sep"]:
                        lines.append(get_sep_line("├", "┼", "┤"))

                lines.append(get_sep_line("└", "┴", "┘"))
                continue
            else:
                line = table_rows[0]
                stripped_line = line.strip()

        # 3. Standard Markdown Elements
        if not stripped_line:
            lines.append("")
        elif stripped_line.startswith("#"):
            heading = re.match(r"^(#{1,6})\s+(.*)$", stripped_line)
            if heading:
                level = len(heading.group(1))
                content = _render_inline_markdown(heading.group(2))
                color = "1;35" if level <= 2 else ("1;36" if level == 3 else "1")
                lines.append(_ansi_wrap(content, color))
            else:
                lines.append(_render_inline_markdown(line))
        elif re.match(r"^\s*[-*+]\s+", line):
            lines.append(f"• {_render_inline_markdown(stripped_line.lstrip('-*+ '))}")
        elif re.match(r"^\s*\d+\.\s+", line):
            lines.append(_render_inline_markdown(line))
        elif stripped_line.startswith(">"):
            lines.append(f"{_ansi_wrap('> ', '90')}{_render_inline_markdown(stripped_line[1:].strip())}")
        elif re.match(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", stripped_line):
            lines.append(_ansi_wrap("─" * 32, "90"))
        else:
            lines.append(_render_inline_markdown(line))
        
        idx += 1

    return "\n".join(lines).strip()








def title(text: str) -> None:
    print(_ansi_wrap(text, "1;35"))


def load_prompt_history(max_items: int = 200) -> List[str]:
    try:
        if not PROMPT_HISTORY_FILE.exists():
            return []
        lines = PROMPT_HISTORY_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
        items = []
        seen = set()
        for line in reversed(lines):
            val = line.strip()
            if not val or val.startswith('#'): continue
            if val not in seen:
                items.append(val)
                seen.add(val)
            if len(items) >= max_items: break
        return list(reversed(items))
    except: return []


def append_prompt_history(val: str, mem: List[str], max_items: int = 200):
    val = val.strip()
    if not val: return
    if val in mem: mem.remove(val)
    mem.append(val)
    if len(mem) > max_items: del mem[:-max_items]
    try: PROMPT_HISTORY_FILE.write_text("\n".join(mem) + "\n", encoding="utf-8")
    except: pass


def resolve_path(raw: str, cwd: Path) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = cwd / candidate
    return candidate.resolve()


def expand_at_file_prompt(user_text: str, cwd: Path) -> str:
    stripped = user_text.strip()
    if not stripped.startswith("@"):
        return user_text

    head, _, tail = stripped[1:].partition(" ")
    file_path = resolve_path(head, cwd)
    file_text = read_file(file_path)
    if tail.strip():
        request_text = tail.strip()
    else:
        request_text = "Review the file content above."

    return (
        f"File: {file_path}\n\n"
        f"Content:\n{file_text}\n\n"
        f"User request: {request_text}"
    )


def read_file(path: Path) -> str:
    if not path.exists():
        return f"Error: file not found: {path}"
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return content[:MAX_TEXT_CHARS] + ("\n... (truncated)" if len(content) > MAX_TEXT_CHARS else "")
    except Exception as exc:
        return f"Error reading file: {exc}"


def write_file(path: Path, content: str) -> str:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except Exception as exc: return f"Error writing file: {exc}"


def list_directory(path: Path) -> str:
    try:
        if not path.is_dir(): return f"Error: {path} is not a directory."
        entries = [f"{item.name}{'/' if item.is_dir() else ''}" for item in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))]
        return "\n".join(entries) if entries else "Directory is empty."
    except Exception as exc: return str(exc)
def search_web(query: str, max_results: int = 5) -> str:
    if not query.strip(): return "Error: query is required."
    max_results = max(1, min(int(max_results or 5), 10))
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as exc: return f"Error: {exc}"

    results: List[str] = []
    pattern = re.compile(r'<a[^>]+class="result__a"[^>]+href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>', re.I | re.S)
    for match in pattern.finditer(raw):
        href = html.unescape(match.group("href"))
        title = html.unescape(re.sub(r"<[^>]+>", "", match.group("title"))).strip()
        parsed = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed.query)
        if "uddg" in params: href = params["uddg"][0]
        if title and href: results.append(f"{len(results)+1}. {title}\n   {href}")
        if len(results) >= max_results: break
    return "\n".join(results) if results else "No results found."


def search_tavily(query: str, tavily_accounts: Dict[str, str], max_results: int = 5) -> str:
    if not query.strip(): return "Error: query is required."
    if not tavily_accounts: return "Error: no Tavily API accounts saved. Use /api to add one."
    max_results = max(1, min(int(max_results or 5), 10))
    errors = []
    for acc_name, api_key in sorted(tavily_accounts.items()):
        payload = {"api_key": api_key, "query": query, "max_results": max_results}
        req = urllib.request.Request("https://api.tavily.com/search", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                body = json.loads(resp.read().decode())
                res_list = body.get("results", [])
                lines = [f"Tavily account: {acc_name}"]
                for i, r in enumerate(res_list[:max_results], 1):
                    lines.append(f"{i}. {r.get('title')}\n   {r.get('url')}\n   {r.get('content')}")
                return "\n".join(lines)
        except Exception as e:
            errors.append(f"{acc_name}: {e}")
    return "Error: Tavily failed.\n" + "\n".join(errors)





def run_powershell_command(command: str, cwd: Path, timeout_seconds: int = 60) -> str:
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            cwd=str(cwd), capture_output=True, text=True, timeout=timeout_seconds
        )
        return ((result.stdout or "") + (result.stderr or "")).strip() or f"Done (exit {result.returncode})"
    except subprocess.TimeoutExpired: return "Error: PowerShell command timed out."
    except Exception as exc: return str(exc)


def search_file(path: Path, query: str, recursive: bool = False, max_results: int = 20) -> str:
    results: List[str] = []
    q_lower = query.lower()
    def scan(f: Path):
        try:
            text = f.read_text(encoding='utf-8', errors='replace')
            for i, line in enumerate(text.splitlines(), 1):
                if q_lower in line.lower():
                    results.append(f"{f}:{i}: {line}")
                    if len(results) >= max_results: return
        except: pass
    if path.is_file(): scan(path)
    else:
        it = path.rglob("*") if recursive else path.iterdir()
        for p in sorted(it):
            if p.is_file(): scan(p)
            if len(results) >= max_results: break
    return "\n".join(results) or "No matches."


def _replace_nth(text: str, old: str, new: str, occurrence: int = 1) -> tuple[str, bool]:
    idx = -1; start = 0
    for _ in range(occurrence):
        idx = text.find(old, start)
        if idx < 0: return text, False
        start = idx + len(old)
    return text[:idx] + new + text[idx + len(old):], True


def smart_replace_block_in_file(path: Path, old_text: str, new_text: str, occurrence: int = 1) -> str:
    if not path.exists(): return f"Error: not found: {path}"
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        updated, found = _replace_nth(content, old_text, new_text, occurrence)
        if found:
            path.write_text(updated, encoding="utf-8")
            return f"Replaced block in {path}"
        # Normalized fallback
        norm_content = content.replace("\r\n", "\n")
        norm_old = old_text.replace("\r\n", "\n")
        updated, found = _replace_nth(norm_content, norm_old, new_text.replace("\r\n", "\n"), occurrence)
        if found:
            path.write_text(updated.replace("\n", "\r\n") if "\r\n" in content else updated, encoding="utf-8")
            return f"Replaced block in {path} (normalized endings)"
        return f"Error: block not found in {path}"
    except Exception as exc: return str(exc)


def replace_lines_in_file(path: Path, start_line: int, end_line: int, new_text: str) -> str:
    if not path.exists(): return f"Error: not found: {path}"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        idx_s = max(0, start_line - 1); idx_e = min(len(lines), end_line)
        lines[idx_s:idx_e] = new_text.splitlines()
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return f"Replaced lines {start_line}-{end_line} in {path}"
    except Exception as exc: return str(exc)


# --- MODEL METADATA & TUI (Ported from Gemini CLI) ---

def model_name(model: Dict[str, Any]) -> str:
    return str(model.get("id", ""))


def short_model_name(model: Dict[str, Any]) -> str:
    name = model_name(model)
    # Strip common provider prefixes and repo paths
    short = name
    if "/" in short:
        short = short.split("/")[-1]
    
    for prefix in ("llama-", "llama3-", "mixtral-", "gemma-", "gemma2-", "llama-3.1-", "llama-3.2-", "llama-3.3-"):
        if short.lower().startswith(prefix):
            short = short[len(prefix):]
            break
    return short.replace("-", " ")


def model_group(model: Dict[str, Any]) -> str:
    name = model_name(model).lower()
    if "llama" in name: return "Llama"
    if "mixtral" in name: return "Mixtral"
    if "gemma" in name: return "Gemma"
    if "whisper" in name: return "Whisper"
    if "qwen" in name: return "Qwen"
    return "Other"


def build_model_table_widths(models: List[Dict[str, Any]]) -> Dict[str, int]:
    short_w = 0; name_w = 0; tag_w = 0; state_w = 0
    for m in models:
        short_w = max(short_w, len(short_model_name(m)))
        name_w = max(name_w, len(model_name(m)))
        tag_w = max(tag_w, len(str(m.get("_tag") or "")))
        state_w = max(state_w, len(str(m.get("_state") or "")))
    return {
        "short": min(max(short_w, 15), 30),
        "name": min(max(name_w, 20), 45),
        "tag": min(max(tag_w, 4), 10),
        "state": min(max(state_w, 6), 16),
    }


def build_model_table_header(widths: Dict[str, int]) -> List[str]:
    return [
        f"  {'Id':>2}  {'Model':<{widths['short']}}  {'Full Name':<{widths['name']}}  {'Uses':>4}  {'Tag':<{widths['tag']}}  Cur  {'State':<{widths['state']}}",
        f"  {'--':>2}  {'-' * widths['short']}  {'-' * widths['name']}  {'-' * 4}  {'-' * widths['tag']}  ---  {'-' * widths['state']}",
    ]


def build_api_account_table_widths(items: List[Dict[str, Any]]) -> Dict[str, int]:
    prov_w = 0; name_w = 0; key_w = 0
    for item in items:
        prov_w = max(prov_w, len(str(item.get("provider", ""))))
        name_w = max(name_w, len(str(item.get("name", ""))))
        key_w = max(key_w, len(str(item.get("masked_key", ""))))
    return {
        "prov": min(max(prov_w, 6), 10),
        "name": min(max(name_w, 10), 28),
        "key": min(max(key_w, 10), 24),
    }


def build_api_account_table_header(widths: Dict[str, int]) -> List[str]:
    return [
        f"  {'Id':>2}  {'Prov':<{widths['prov']}}  {'Account':<{widths['name']}}  {'Key':<{widths['key']}}  State",
        f"  {'--':>2}  {'-' * widths['prov']}  {'-' * widths['name']}  {'-' * widths['key']}  -----",
    ]


def format_api_account_entry(
    index: int,
    item: Dict[str, Any],
    widths: Dict[str, int],
    selected: bool = False,
) -> str:
    action = str(item.get("action", "load"))
    provider = str(item.get("provider", ""))
    name = str(item.get("name", ""))
    key = str(item.get("masked_key", ""))
    state = str(item.get("state", ""))
    marker = ">" if selected else " "
    row = (
        f"{marker} {index:>2}  "
        f"{provider:<{widths['prov']}}  "
        f"{name:<{widths['name']}}  "
        f"{key:<{widths['key']}}  "
        f"{state}"
    ).rstrip()
    if selected:
        return _ansi_wrap(row, "48;5;24;97")
    if action == "add":
        return _ansi_wrap(row, "32")
    return row


def pick_api_account_interactive(
    accounts: Dict[str, str],
    tavily_accounts: Dict[str, str],
    active_api_account: str = "",
    title_text: str = "Manage API Accounts",
) -> Optional[Dict[str, str]]:
    items: List[Dict[str, Any]] = [
        {"action": "add", "provider": "groq", "name": "Add Groq API", "masked_key": "", "state": "new"},
        {"action": "add", "provider": "tavily", "name": "Add Tavily API", "masked_key": "", "state": "new"}
    ]
    for name, key in sorted(accounts.items(), key=lambda item: item[0].lower()):
        masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
        state = "active" if name == active_api_account else "saved"
        items.append({"action": "load", "provider": "groq", "name": name, "masked_key": masked, "state": state})
    for name, key in sorted(tavily_accounts.items(), key=lambda item: item[0].lower()):
        masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
        items.append({"action": "load", "provider": "tavily", "name": name, "masked_key": masked, "state": "saved"})
    widths = build_api_account_table_widths(items)

    def render_item(item: Dict[str, Any], _: int, selected: bool = False) -> str:
        return format_api_account_entry(_ + 1, item, widths, selected=selected)

    chosen = interactive_select(
        title_text=title_text,
        items=items,
        render_item=render_item,
    )
    if not chosen:
        return None
    return {
        "action": str(chosen["action"]),
        "provider": str(chosen["provider"]),
        "name": str(chosen["name"]),
    }



def format_model_entry(
    index: int,
    model: Dict[str, Any],
    current_model: str,
    widths: Dict[str, int],
    selected: bool = False,
) -> str:
    name = model_name(model)
    display_name = short_model_name(model)
    active = "*" if name == current_model else " "
    tag = str(model.get("_tag") or "")
    usage = int(model.get("_uses") or 0)
    state = str(model.get("_state") or "")
    if state.startswith("cooldown"):
        state = _ansi_wrap(state, "31")
    marker = ">" if selected else " "
    
    # Constrain strings to calculated widths to prevent overflow
    disp_clipped = display_name[:widths['short']]
    name_clipped = name[:widths['name']]
    
    row = (
        f"{marker} {index:>2}  "
        f"{disp_clipped:<{widths['short']}}  "
        f"{name_clipped:<{widths['name']}}  "
        f"{usage:>4}  "
        f"{tag:<{widths['tag']}}  "
        f"{active}  "
        f"{state:<{widths['state']}}"
    ).rstrip()
    
    if selected: return _ansi_wrap(row, "48;5;24;97")
    if name == current_model: return _ansi_wrap(row, "32")
    if model.get("_hidden"): return _ansi_wrap(row, "2")
    return row


# --- TOOL MANAGEMENT (Ported from Gemini CLI) ---

def list_tool_catalog() -> List[Dict[str, Any]]:
    try:
        if TOOLS_FILE.exists():
            data = json.loads(TOOLS_FILE.read_text(encoding="utf-8"))
            return data
    except: pass
    return []


def build_tool_table_header() -> List[str]:
    return [
        f"  {'Id':>2}  {'Tool':<25}  State",
        f"  {'--':>2}  {'-' * 25}  -----",
    ]


def format_tool_entry(index: int, tool: Dict[str, Any], disabled: Set[str], selected: bool = False) -> str:
    name = tool['function']['name']
    is_enabled = name not in disabled
    marker = ">" if selected else " "
    state = _ansi_wrap("on", "32") if is_enabled else _ansi_wrap("off", "31")
    
    row = f"{marker} {index:>2}  {name:<25}  {state}"
    if selected: return _ansi_wrap(row, "48;5;24;97")
    return row


def pick_tool_interactive(disabled_tools: Set[str]) -> bool:
    catalog = list_tool_catalog()
    if not catalog:
        error("No tools found in tools.json")
        return False

    categories = sorted(list(set(t.get('category', 'Other') for t in catalog)))
    changed = False

    while True:
        cat_items = []
        for cat in categories:
            # Ensure we use the same default 'Other' when filtering tools for the category view
            tools_in_cat = [t for t in catalog if t.get('category', 'Other') == cat]
            enabled_count = sum(1 for t in tools_in_cat if t['function']['name'] not in disabled_tools)
            cat_items.append({
                "name": cat,
                "label": f"=== {cat} ({enabled_count}/{len(tools_in_cat)} active) ==="
            })

        chosen_cat = interactive_select("Manage Tools - Categories", cat_items, 
            lambda item, i, sel: _ansi_wrap(f"{'> ' if sel else '  '}{item['label']}", "1;36" if not sel else "48;5;24;97"))
        
        if not chosen_cat: break

        # Sub-menu for tools in category
        cat_name = chosen_cat['name']
        tools_in_cat = [t for t in catalog if t.get('category') == cat_name]
        
        while True:
            def render_tool(t, i, sel):
                return format_tool_entry(i+1, t, disabled_tools, sel)

            def toggle_tool(t, i):
                nonlocal changed
                name = t['function']['name']
                if name in disabled_tools: disabled_tools.remove(name)
                else: disabled_tools.add(name)
                changed = True

            # Modified interactive_select to support toggling with Space
            clear_screen(); title(f"Tools: {cat_name}")
            print("Use Up/Down, Space to toggle, Enter/Esc to return.\n")
            for line in build_tool_table_header(): print(line)
            
            # Simple manual loop for the sub-menu to allow Space key
            idx = 0
            while True:
                clear_screen(); title(f"Tools: {cat_name}")
                print("Use Up/Down, Space to toggle, Enter/Esc to return.\n")
                for line in build_tool_table_header(): print(line)
                for i, t in enumerate(tools_in_cat):
                    print(render_tool(t, i, i == idx))
                
                # Show info footer
                cur = tools_in_cat[idx]
                print(f"\nInfo: {cur['function']['description']}")
                if cur.get('rating'): print(f"Advice: {cur['rating']}")

                k = read_key()
                if k in ("\r", "\n", "\x1b"): break
                if k == " ": toggle_tool(tools_in_cat[idx], idx)
                if k in ("\xe0H", "\x00H"): idx = (idx - 1) % len(tools_in_cat)
                elif k in ("\xe0P", "\x00P"): idx = (idx + 1) % len(tools_in_cat)
            break
            
    return changed



class GroqClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(
        self,
        messages: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        history = []
        if system_instruction:
            history.append({"role": "system", "content": system_instruction})
        history.extend(messages)
        payload = {"model": self.model, "messages": history, "temperature": temperature}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        request = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "Mozilla/5.0 GroqCLI/1.0"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
                msg = body.get("error", {}).get("message", raw)
            except: msg = raw
            raise RuntimeError(f"Groq API Error: {msg}") from exc

    def list_models(self) -> List[Dict[str, Any]]:
        url = "https://api.groq.com/openai/v1/models"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.api_key}", "User-Agent": "GroqCLI/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8")).get("data", [])


def execute_tool(name: str, args: Dict[str, Any], cwd: Path, tavily_accounts: Optional[Dict[str, str]] = None) -> str:
    if name == "read_file": return read_file(resolve_path(args.get("filepath", ""), cwd))
    if name == "write_file": return write_file(resolve_path(args.get("filepath", ""), cwd), args.get("content", ""))
    if name == "list_directory": return list_directory(resolve_path(args.get("path", "."), cwd))
    if name == "get_system_info": return f"OS: {platform.system()} | CWD: {cwd}"
    if name == "search_file": return search_file(resolve_path(args.get("path", "."), cwd), str(args.get("query", "")), bool(args.get("recursive", False)))
    if name == "search_web": return search_web(str(args.get("query", "")), int(args.get("max_results", 5) or 5))
    if name == "search_tavily": return search_tavily(str(args.get("query", "")), tavily_accounts or {}, int(args.get("max_results", 5) or 5))
    if name == "run_powershell": return run_powershell_command(str(args.get("command", "")), cwd, int(args.get("timeout_seconds", 60) or 60))
    if name == "smart_replace_block": return smart_replace_block_in_file(resolve_path(args.get("filepath", ""), cwd), str(args.get("old_text", "")), str(args.get("new_text", "")), int(args.get("occurrence", 1) or 1))
    if name == "replace_lines": return replace_lines_in_file(resolve_path(args.get("filepath", ""), cwd), int(args.get("start_line", 1)), int(args.get("end_line", 1)), str(args.get("new_text", "")))
    if name == "request_follow_up": return f"Turn granted: {args.get('reason')}"
    return f"Unknown tool: {name}"


def _require_api_crypto():
    if not all([AES, PBKDF2, get_random_bytes]): raise RuntimeError("pycryptodome required.")

def _encrypt_api_accounts(accounts: Dict[str, str], password: str, tavily_accounts: Optional[Dict[str, str]] = None) -> bytes:
    _require_api_crypto()
    payload = json.dumps({
        "accounts": accounts,
        "tavily_accounts": tavily_accounts or {}
    }, indent=2).encode("utf-8")
    salt = get_random_bytes(16)
    key = PBKDF2(password.encode(), salt, dkLen=32, count=200_000)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(payload)
    def pack(b): return len(b).to_bytes(4, 'big') + b
    return API_ACCOUNTS_MAGIC + pack(salt) + pack(cipher.nonce) + pack(tag) + pack(ciphertext)

def _decrypt_api_accounts(blob: bytes, password: str) -> Dict[str, Any]:
    _require_api_crypto()
    if not blob.startswith(API_ACCOUNTS_MAGIC): raise ValueError("Invalid lock file.")
    def unpack(b, o):
        s = int.from_bytes(b[o:o+4], 'big')
        return b[o+4:o+4+s], o+4+s
    o = len(API_ACCOUNTS_MAGIC)
    salt, o = unpack(blob, o); nonce, o = unpack(blob, o); tag, o = unpack(blob, o); ct, o = unpack(blob, o)
    key = PBKDF2(password.encode(), salt, dkLen=32, count=200_000)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = json.loads(cipher.decrypt_and_verify(ct, tag).decode())
    if not isinstance(data, dict): data = {"accounts": {}}
    if "accounts" not in data: data = {"accounts": data, "tavily_accounts": {}}
    if "tavily_accounts" not in data: data["tavily_accounts"] = {}
    return data


def test_model(client: GroqClient, model_id: str) -> str:
    test_client = GroqClient(client.api_key, model_id)
    try:
        resp = test_client.generate([{"role": "user", "content": "Say exactly: OK"}], system_instruction="Reply OK only.", temperature=0.0)
        content = resp["choices"][0]["message"]["content"]
        return _clean_response_text(content)
    except Exception as e: return f"Error: {e}"


def read_key() -> str:
    if msvcrt is None: return input().strip()
    ch = msvcrt.getwch()
    if ch in ("\x00", "\xe0"): return ch + msvcrt.getwch()
    return ch


def clear_screen():
    if sys.stdout.isatty(): os.system("cls" if os.name == "nt" else "clear")


def interactive_select(title_text: str, items: List[Any], render_item: Callable[[Any, int, bool], str]) -> Optional[Any]:
    if not items: return None
    idx = 0
    while True:
        clear_screen(); title(title_text); print("Use Up/Down, Enter to select, Esc to cancel.\n")
        for i, item in enumerate(items):
            print(render_item(item, i, i == idx))
        k = read_key()
        if k in ("\r", "\n"): return items[idx]
        if k == "\x1b": return None
        if k in ("\xe0H", "\x00H"): idx = (idx - 1) % len(items)
        elif k in ("\xe0P", "\x00P"): idx = (idx + 1) % len(items)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key")
    parser.add_argument("--password")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    # Load Preferences
    prefs = {}
    if MODEL_PREFS_FILE.exists():
        try: prefs = json.loads(MODEL_PREFS_FILE.read_text(encoding="utf-8"))
        except: pass

    hidden_models = list(prefs.get("hidden_models", []))
    speed_tags = dict(prefs.get("speed_tags", {}))
    model_usage_counts = dict(prefs.get("model_usage_counts", {}))
    disabled_tools = set(prefs.get("disabled_tools", []))
    last_model = str(prefs.get("last_model") or DEFAULT_MODEL)
    last_api_account = str(prefs.get("last_api_account") or "")
    system_instruction = str(prefs.get("system_instruction") or DEFAULT_SYSTEM)

    api_accounts = {}
    tavily_accounts = {}
    if API_ACCOUNTS_FILE.exists():
        pwd = args.password or getpass.getpass("Groq Lock Password: ")
        try:
            decrypted = _decrypt_api_accounts(API_ACCOUNTS_FILE.read_bytes(), pwd)
            api_accounts = decrypted.get("accounts", {})
            tavily_accounts = decrypted.get("tavily_accounts", {})
        except: error("Failed to unlock API accounts."); return 1

    active_api_account = ""
    api_key = args.api_key or os.environ.get("GROQ_API_KEY")
    
    if not api_key and api_accounts:
        active_api_account = last_api_account if last_api_account in api_accounts else next(iter(sorted(api_accounts.keys(), key=str.lower)))
        api_key = api_accounts[active_api_account]

    if not api_key:
        error("No API key found. Start with --api-key or use /api.")
        api_key = "placeholder"

    active_model = args.model or last_model
    client = GroqClient(api_key, active_model)
    messages: List[Dict[str, Any]] = []
    cwd = Path.cwd()
    model_cooldowns: Dict[str, dt.datetime] = {}
    # Load tools and prepare initial active list
    all_tools = json.loads(TOOLS_FILE.read_text(encoding="utf-8")) if TOOLS_FILE.exists() else []
    tools = [t for t in all_tools if t['function']['name'] not in disabled_tools]
    history = load_prompt_history()

    def persist_selection():
        payload = {
            "hidden_models": sorted(set(hidden_models)),
            "speed_tags": speed_tags,
            "model_usage_counts": model_usage_counts,
            "disabled_tools": sorted(list(disabled_tools)),
            "last_model": client.model,
            "last_api_account": active_api_account,
            "system_instruction": system_instruction,
        }
        MODEL_PREFS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def record_usage(m_id: str):
        model_usage_counts[m_id] = model_usage_counts.get(m_id, 0) + 1
        persist_selection()

    title("Groq Terminal CLI (Fully Functional Port)")
    info(f"Model: {client.model} | Root: {cwd}")

    def prune_model_cooldowns():
        expired = [name for name, until in model_cooldowns.items() if until <= _now()]
        for name in expired:
            model_cooldowns.pop(name, None)
            write_notification()

    def get_prompt():
        prune_model_cooldowns()
        prefix = f"groq:{client.model.split('-')[0]}"
        cooldown_text = format_cooldown_until(model_cooldowns.get(client.model))
        if cooldown_text:
            prefix += f" [{cooldown_text}]"
        return _ansi_wrap(f"{prefix}> ", "1;32")

    while True:
        try:
            user_input = read_dynamic_prompt(get_prompt, history, cwd=cwd).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            user_input = "continue"
            info("continue")
        
        append_prompt_history(user_input, history)

        if user_input.startswith("/"):
            parts = user_input.split()
            cmd = parts[0].lower()
            rem = " ".join(parts[1:])
            
            if cmd == "/exit": break
            if cmd == "/reset": messages = []; info("Reset."); continue
            if cmd == "/mm":
                try:
                    prune_model_cooldowns()
                    raw_models = client.list_models()
                    # Filter and decorate
                    decorated = []
                    for m in raw_models:
                        m_id = m['id']
                        copy_m = dict(m)
                        copy_m["_tag"] = speed_tags.get(m_id, "")
                        copy_m["_uses"] = model_usage_counts.get(m_id, 0)
                        copy_m["_hidden"] = m_id in hidden_models
                        cooldown_text = format_cooldown_until(model_cooldowns.get(m_id))
                        copy_m["_state"] = cooldown_text or ("hidden" if copy_m["_hidden"] else "")
                        decorated.append(copy_m)
                    
                    decorated.sort(key=lambda x: (model_group(x), x['id']))
                    
                    # If arg provided, try to switch directly
                    if rem:
                        target = rem.strip()
                        if target.isdigit():
                            idx = int(target) - 1
                            if 0 <= idx < len(decorated):
                                client.model = decorated[idx]['id']
                                info(f"Switched to {client.model}"); persist_selection()
                                continue
                        # Match by name
                        for m in decorated:
                            if target in m['id']:
                                client.model = m['id']
                                info(f"Switched to {client.model}"); persist_selection()
                                break
                        continue

                    # Otherwise, show interactive TUI
                    widths = build_model_table_widths(decorated)
                    print()
                    for line in build_model_table_header(widths): print(line)
                    
                    chosen = interactive_select("Select Model", decorated, 
                        lambda m, i, sel: format_model_entry(i+1, m, client.model, widths, sel))
                    
                    if chosen:
                        client.model = chosen['id']
                        info(f"Model set to {client.model}"); persist_selection()
                except Exception as e: error(str(e))
                continue
            if cmd == "/test":
                info("Testing all models and auto-hiding failures...")
                try:
                    raw_models = client.list_models()
                    passed_any = False
                    for m in raw_models:
                        m_id = m['id']
                        print(f"- {m_id} ... ", end="", flush=True)
                        start_t = time.perf_counter()
                        res = test_model(client, m_id)
                        elapsed = time.perf_counter() - start_t
                        
                        if res == "OK":
                            print(_ansi_wrap(f"OK ({elapsed:.2f}s)", "32"))
                            if m_id in hidden_models: hidden_models.remove(m_id)
                            passed_any = True
                        else:
                            print(_ansi_wrap(f"FAIL ({res})", "31"))
                            if m_id not in hidden_models: hidden_models.append(m_id)
                    
                    persist_selection()
                    if passed_any: info("Tests complete. Hidden models updated.")
                except Exception as e: error(str(e))
                continue
            if cmd == "/api":
                chosen_api = pick_api_account_interactive(api_accounts, tavily_accounts, active_api_account)
                if not chosen_api: continue
                
                prov = chosen_api["provider"]
                if chosen_api["action"] == "add":
                    name = input(f"{prov.title()} API name: ").strip()
                    if not name: continue
                    key = input(f"{prov.title()} API key: ").strip()
                    if not key: continue
                    
                    pwd = args.password or getpass.getpass("Password to protect API file: ")
                    if prov == "tavily": tavily_accounts[name] = key
                    else: api_accounts[name] = key
                    
                    try:
                        API_ACCOUNTS_FILE.write_bytes(_encrypt_api_accounts(api_accounts, pwd, tavily_accounts))
                        if prov == "groq":
                            active_api_account = name
                            client.api_key = key
                            persist_selection()
                        info(f"Added {prov} account: {name}")
                    except Exception as e: error(f"Failed to save: {e}")
                elif prov == "tavily":
                    info(f"Tavily account: {chosen_api['name']} (Key: {tavily_accounts[chosen_api['name']][:4]}...)")
                else:
                    active_api_account = chosen_api["name"]
                    client.api_key = api_accounts[active_api_account]
                    persist_selection()
                    info(f"Switched to API account: {active_api_account}")
                continue
            if cmd == "/system":
                if rem: system_instruction = rem; info("System instruction updated.")
                else: print(f"Current System Instruction:\n{system_instruction}")
                continue
            if cmd == "/save":
                if not rem: warn("Usage: /save <filename>"); continue
                Path(rem).write_text(json.dumps({"messages": messages, "model": client.model, "system": system_instruction}, indent=2))
                info(f"Saved transcript to {rem}")
                continue
            if cmd == "/load":
                if not rem or not Path(rem).exists(): warn("Usage: /load <valid_file>"); continue
                data = json.loads(Path(rem).read_text())
                messages = data.get("messages", [])
                client.model = data.get("model", client.model)
                system_instruction = data.get("system", system_instruction)
                info(f"Loaded transcript from {rem}")
                continue
            if cmd == "/tool":
                if pick_tool_interactive(disabled_tools):
                    persist_selection()
                    info("Tool settings updated.")
                continue
            
            warn(f"Commands: /mm, /test, /tool, /api, /system, /save, /load, /reset, /exit")
            continue

        expanded_input = expand_at_file_prompt(user_input, cwd)
        messages.append({"role": "user", "content": expanded_input})
        
        for _ in range(DEFAULT_TOOL_LOOPS):
            try:
                # Refresh active tools each turn to respect changes made via /tool
                active_tools = [t for t in all_tools if t['function']['name'] not in disabled_tools]
                response = client.generate(messages, system_instruction=system_instruction, tools=active_tools)
                record_usage(client.model)
            except RuntimeError as exc:
                msg = str(exc)
                error(msg)
                match = re.search(r"try again in ([0-9]+(?:\.[0-9]+)?)s", msg, re.IGNORECASE)
                if match:
                    wait_seconds = float(match.group(1))
                    # Set cooldown for 1 minute or the requested time, whichever is longer
                    cooldown_duration = max(60.0, wait_seconds)
                    model_cooldowns[client.model] = _now() + dt.timedelta(seconds=cooldown_duration)
                    warn(f"Cooldown set for {client.model}: {format_cooldown_until(model_cooldowns.get(client.model))}")
                    write_notification()
                break
            except Exception as e:
                error(str(e))
                break
                
            msg = response["choices"][0]["message"]
            
            # Sanitize message for cross-model compatibility by removing reasoning/think fields
            sanitized_msg = {
                "role": msg.get("role"),
                "content": msg.get("content")
            }
            if msg.get("tool_calls"):
                sanitized_msg["tool_calls"] = msg.get("tool_calls")
            
            messages.append(sanitized_msg)
            
            if msg.get("content"):
                cleaned_text = _clean_response_text(msg['content'])
                if cleaned_text:
                    print()
                    print(render_markdown_text(cleaned_text))
                    print()
            if not msg.get("tool_calls"): write_notification(); break
                
            for tool_call in msg["tool_calls"]:
                t_id = tool_call["id"]
                t_name = tool_call["function"]["name"]
                try: t_args = json.loads(tool_call["function"]["arguments"])
                except: t_args = {}
                
                info(f"[tool] {t_name}")
                result = execute_tool(t_name, t_args, cwd, tavily_accounts=tavily_accounts)
                messages.append({"role": "tool", "tool_call_id": t_id, "content": result})
                info(f"[result] {str(result)[:80]}...")

    return 0

if Completer is not None:
    class GroqCliCompleter(Completer):
        SLASH_COMMANDS = [
            ("/help", "Show available commands"),
            ("/exit", "Quit CLI"),
            ("/quit", "Quit CLI"),
            ("/reset", "Clear conversation history"),
            ("/mm", "Open model picker / switch model"),
            ("/test", "Test all models"),
            ("/api", "Open API account picker"),
            ("/tool", "Open tool manager"),
            ("/system", "Replace or load system instruction"),
            ("/save", "Save transcript JSON"),
            ("/load", "Load transcript JSON"),
        ]

        def __init__(self, cwd: Optional[Path] = None):
            self.cwd = Path(cwd) if cwd else Path.cwd()

        def _get_path_completions(self, raw_path: str) -> List[tuple[str, str, str]]:
            raw_path = raw_path.replace("\\", "/")
            if "/" in raw_path:
                dir_part, _, search_part = raw_path.rpartition("/")
            else:
                dir_part, search_part = "", raw_path

            if dir_part:
                p_dir = Path(dir_part)
                if p_dir.is_absolute() or dir_part.startswith("~"):
                    target_dir = p_dir.expanduser()
                else:
                    target_dir = self.cwd / dir_part
            else:
                target_dir = self.cwd

            if not target_dir.exists() or not target_dir.is_dir():
                return []

            results: List[tuple[str, str, str]] = []
            try:
                for entry in sorted(target_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                    name = entry.name
                    if name.startswith(".") and not search_part.startswith("."):
                        continue
                    if name == "__pycache__" and not search_part.startswith("__"):
                        continue
                    if not search_part or search_part.lower() in name.lower():
                        is_dir = entry.is_dir()
                        item_name = name + ("/" if is_dir else "")
                        full_rel = f"{dir_part}/{item_name}" if dir_part else item_name
                        meta = "Directory" if is_dir else "File"
                        results.append((full_rel, item_name, meta))
            except Exception:
                pass
            return results

        def get_completions(self, document, complete_event):
            text = document.text_before_cursor

            # 1. Slash commands at start of line
            if text.startswith("/"):
                if " " not in text:
                    for cmd, desc in self.SLASH_COMMANDS:
                        if cmd.lower().startswith(text.lower()) or text.lower() in cmd.lower():
                            yield Completion(
                                cmd,
                                start_position=-len(text),
                                display=cmd,
                                display_meta=desc,
                            )
                    return
                else:
                    cmd_part, _, arg_part = text.partition(" ")
                    cmd_lower = cmd_part.lower()
                    if cmd_lower in {"/save", "/load", "/system"}:
                        for full_rel, display_name, meta in self._get_path_completions(arg_part):
                            yield Completion(
                                full_rel,
                                start_position=-len(arg_part),
                                display=display_name,
                                display_meta=meta,
                            )
                        return

            # 2. @ file and folder completions anywhere in the line
            last_at = text.rfind("@")
            if last_at != -1:
                after_at = text[last_at + 1 :]
                if " " not in after_at and "\t" not in after_at:
                    for full_rel, display_name, meta in self._get_path_completions(after_at):
                        yield Completion(
                            full_rel,
                            start_position=-len(after_at),
                            display=display_name,
                            display_meta=meta,
                        )
else:
    GroqCliCompleter = None


def read_dynamic_prompt(
    prompt_provider: Callable[[], str],
    history: Optional[List[str]] = None,
    cwd: Optional[Path] = None,
) -> str:
    if pt_prompt is not None and ANSI is not None and InMemoryHistory is not None and CompleteStyle is not None and Style is not None:
        prompt_history = InMemoryHistory(history or [])
        completer = GroqCliCompleter(cwd=cwd) if GroqCliCompleter is not None else None
        user_style = Style.from_dict({'': 'ansired'})
        
        return pt_prompt(
            message=lambda: ANSI(prompt_provider()),
            history=prompt_history,
            auto_suggest=AutoSuggestFromHistory() if AutoSuggestFromHistory is not None else None,
            completer=completer,
            complete_while_typing=True,
            complete_style=CompleteStyle.COLUMN,
            mouse_support=False,
            wrap_lines=True,
            refresh_interval=0.25,
            style=user_style,
        )
    return input(prompt_provider())


if __name__ == "__main__":
    raise SystemExit(main())
