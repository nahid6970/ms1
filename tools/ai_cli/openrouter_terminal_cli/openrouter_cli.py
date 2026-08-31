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
import urllib.error
import urllib.parse
import urllib.request
import unicodedata
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Protocol.KDF import PBKDF2
    from Cryptodome.Random import get_random_bytes
except Exception:
    AES = PBKDF2 = get_random_bytes = None

DEFAULT_MODEL = "google/gemini-2.0-flash-exp:free"
DEFAULT_SYSTEM = (
    "You are a terminal coding assistant using OpenRouter. "
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
API_ACCOUNTS_MAGIC = b"ORAPI1"
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
    pt_prompt = AutoSuggestFromHistory = Completer = Completion = ANSI = InMemoryHistory = CompleteStyle = Style = None

# --- UTILS ---

def _now_stamp() -> str: return dt.datetime.now().strftime("%Y-%m-%d-%H:%M")
def _now() -> dt.datetime: return dt.datetime.now()

def write_notification() -> None:
    try: NOTIFICATION_FILE.write_text(_now_stamp(), encoding="utf-8")
    except Exception: pass

def _ansi_wrap(text: str, code: str) -> str:
    if not sys.stdout.isatty(): return text
    return f"\033[{code}m{text}\033[0m"

def info(text: str) -> None: print(_ansi_wrap(text, "36"))
def warn(text: str) -> None: print(_ansi_wrap(text, "33"))
def error(text: str) -> None: print(_ansi_wrap(text, "31"))
def title(text: str) -> None: print(_ansi_wrap(text, "1;35"))

def _visible_len(text: str) -> int:
    clean_text = re.sub(r'\x1b\[[0-9;]*[mK]', '', text)
    width = 0
    for char in clean_text:
        if unicodedata.east_asian_width(char) in ('W', 'F'): width += 2
        else: width += 1
    return width

def _format_seconds(seconds: float) -> str:
    total = max(0, int(seconds + 0.999))
    minutes, secs = divmod(total, 60)
    return f"{minutes:02d}:{secs:02d}"

def format_cooldown_until(until: Optional[dt.datetime]) -> str:
    if until is None: return ""
    remaining = int((until - _now()).total_seconds() + 0.999)
    if remaining <= 0: return ""
    return f"cooldown {_format_seconds(remaining)}"

def _clean_response_text(text: str) -> str:
    if not text: return ""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

# --- FILE & SYSTEM HELPERS ---

def resolve_path(raw: str, cwd: Path) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute(): candidate = cwd / candidate
    return candidate.resolve()

def read_file(path: Path) -> str:
    if not path.exists(): return f"Error: file not found: {path}"
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return content[:MAX_TEXT_CHARS] + ("\n... (truncated)" if len(content) > MAX_TEXT_CHARS else "")
    except Exception as exc: return f"Error reading file: {exc}"

def write_file(path: Path, content: str) -> str:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except Exception as exc: return str(exc)

def list_directory(path: Path) -> str:
    try:
        if not path.is_dir(): return f"Error: {path} is not a directory."
        entries = [f"{item.name}{'/' if item.is_dir() else ''}" for item in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))]
        return "\n".join(entries) if entries else "Directory is empty."
    except Exception as exc: return str(exc)

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
    results = []; q_lower = query.lower()
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

def search_web(query: str, max_results: int = 5) -> str:
    if not query.strip(): return "Error: query is required."
    max_results = max(1, min(int(max_results or 5), 10))
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as exc: return f"Error: {exc}"
    results = []
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
    if not tavily_accounts: return "Error: no Tavily accounts. Use /api."
    max_results = max(1, min(int(max_results or 5), 10))
    errors = []
    for name, key in sorted(tavily_accounts.items()):
        payload = {"api_key": key, "query": query, "max_results": max_results}
        req = urllib.request.Request("https://api.tavily.com/search", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                body = json.loads(resp.read().decode())
                res = body.get("results", [])
                lines = [f"Tavily: {name}"]
                for i, r in enumerate(res[:max_results], 1):
                    lines.append(f"{i}. {r.get('title')}\n   {r.get('url')}\n   {r.get('content')}")
                return "\n".join(lines)
        except Exception as e: errors.append(f"{name}: {e}")
    return "Error: Tavily failed.\n" + "\n".join(errors)

def replace_lines_in_file(path: Path, start_line: int, end_line: int, new_text: str) -> str:
    if not path.exists(): return f"Error: not found: {path}"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        idx_s = max(0, start_line - 1); idx_e = min(len(lines), end_line)
        lines[idx_s:idx_e] = new_text.splitlines()
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return f"Replaced lines {start_line}-{end_line} in {path}"
    except Exception as exc: return str(exc)

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
        norm_content = content.replace("\r\n", "\n")
        updated, found = _replace_nth(norm_content, old_text.replace("\r\n", "\n"), new_text.replace("\r\n", "\n"), occurrence)
        if found:
            path.write_text(updated.replace("\n", "\r\n") if "\r\n" in content else updated, encoding="utf-8")
            return f"Replaced block in {path} (normalized)"
        return f"Error: block not found in {path}"
    except Exception as exc: return str(exc)

def _patch_path(raw: str, cwd: Path) -> Optional[Path]:
    raw = raw.strip()
    if raw == "/dev/null": return None
    if "\t" in raw: raw = raw.split("\t", 1)[0]
    if " " in raw: raw = raw.split(" ", 1)[0]
    if raw.startswith("a/") or raw.startswith("b/"): raw = raw[2:]
    return resolve_path(raw, cwd)

def _parse_hunk_header(line: str) -> Optional[tuple[int, int, int, int]]:
    match = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
    if not match: return None
    return int(match.group(1)), int(match.group(2) or "1"), int(match.group(3)), int(match.group(4) or "1")

def apply_fuzzy_unified_patch(patch_text: str, cwd: Path) -> str:
    if not patch_text.strip(): return "Error: patch required."
    lines = patch_text.replace("\r\n", "\n").split("\n")
    file_patches = []; i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("--- "):
            old_p = _patch_path(line[4:].strip(), cwd); i += 1
            if i >= len(lines) or not lines[i].startswith("+++ "): return "Error: expected +++."
            new_p = _patch_path(lines[i][4:].strip(), cwd); i += 1
            hunks = []
            while i < len(lines) and not lines[i].startswith("--- "):
                if not lines[i].startswith("@@ "): i += 1; continue
                hunk = [lines[i]]; i += 1
                while i < len(lines) and not lines[i].startswith("@@ ") and not lines[i].startswith("--- "):
                    if not lines[i].startswith("\\ "): hunk.append(lines[i])
                    i += 1
                hunks.append(hunk)
            file_patches.append({"old": old_p, "new": new_p, "hunks": hunks})
        else: i += 1
    if not file_patches: return "Error: no patches found."
    updates = {}; touched = []
    for fp in file_patches:
        target = fp["new"] or fp["old"]
        if target.exists(): original = target.read_text(encoding="utf-8", errors="replace").splitlines()
        else: original = []
        res_lines = list(original); offset = 0
        for hunk in fp["hunks"]:
            parsed = _parse_hunk_header(hunk[0])
            if not parsed: return f"Error: malformed header: {hunk[0]}"
            old_s, _, _, _ = parsed; pos = max(old_s - 1 + offset, 0)
            old_seg = []; new_seg = []
            for h_l in hunk[1:]:
                if h_l.startswith(" "): old_seg.append(h_l[1:]); new_seg.append(h_l[1:])
                elif h_l.startswith("-"): old_seg.append(h_l[1:])
                elif h_l.startswith("+"): new_seg.append(h_l[1:])
            # Fuzzy search window
            found_p = -1; radius = 50
            for cand in range(max(0, pos-radius), min(len(res_lines)-len(old_seg)+1, pos+radius+1)):
                if [l.rstrip() for l in res_lines[cand:cand+len(old_seg)]] == [l.rstrip() for l in old_seg]:
                    found_p = cand; break
            if found_p == -1: return f"Error: patch context mismatch in {target}."
            res_lines[found_p:found_p+len(old_seg)] = new_seg
            offset += len(new_seg) - len(old_seg)
        updates[target] = "\n".join(res_lines) + ("\n" if res_lines else ""); touched.append(target)
    for p, c in updates.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(c, encoding="utf-8")
    return "Applied:\n" + "\n".join(str(p) for p in touched)

# --- MARKDOWN RENDERER ---

def _render_inline_markdown(text: str) -> str:
    if not text: return text
    def repl_l(m):
        if sys.stdout.isatty(): return f"{_ansi_wrap(m.group(1), '4;36')} ({m.group(2)})"
        return f"{m.group(1)} ({m.group(2)})"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl_l, text)
    text = re.sub(r"(?<!\*)\*\*(.+?)\*\*(?!\*)", lambda m: _ansi_wrap(m.group(1), "1"), text)
    text = re.sub(r"(?<!_)__(.+?)__(?!_)", lambda m: _ansi_wrap(m.group(1), "1"), text)
    text = re.sub(r"(\s|^|[(\[{])\*(?!\s)(.+?)(?<!\s)\*(\s|$|[.,!?;:)}\]])", lambda m: f"{m.group(1)}{_ansi_wrap(m.group(2), '3')}{m.group(3)}", text)
    text = re.sub(r"(\s|^|[(\[{])_(?!\s)(.+?)(?<!\s)_(\s|$|[.,!?;:)}\]])", lambda m: f"{m.group(1)}{_ansi_wrap(m.group(2), '3')}{m.group(3)}", text)
    text = re.sub(r"`([^`]+)`", lambda m: _ansi_wrap(m.group(1), "38;5;214"), text)
    return text

def _wrap_visible(text: str, max_w: int) -> List[str]:
    if _visible_len(text) <= max_w: return [text]
    words = text.split(' '); lines = []; cur_l = []; cur_len = 0
    for w in words:
        w_l = _visible_len(w)
        if cur_len + w_l + (1 if cur_l else 0) <= max_w: cur_l.append(w); cur_len += w_l + (1 if cur_l else 0)
        else:
            if cur_l: lines.append(' '.join(cur_l))
            cur_l = [w]; cur_len = w_l
    if cur_l: lines.append(' '.join(cur_l))
    return lines

def render_markdown_text(text: str) -> str:
    lines = []; in_code = False; raw = text.splitlines(); idx = 0
    try: term_w = os.get_terminal_size().columns
    except: term_w = 100
    while idx < len(raw):
        line = raw[idx]; stripped = line.strip()
        fence = re.match(r"^\s*```(\w+)?\s*$", line)
        if fence: in_code = not in_code; lines.append(_ansi_wrap(line, "90")); idx += 1; continue
        if in_code: lines.append(f"  {line}"); idx += 1; continue
        if "|" in stripped:
            rows = []
            while idx < len(raw) and "|" in raw[idx]: rows.append(raw[idx]); idx += 1
            if len(rows) >= 2:
                grid = []
                for r in rows:
                    content = r.strip(); 
                    if content.startswith("|"): content = content[1:]
                    if content.endswith("|"): content = content[:-1]
                    cells = [c.strip() for c in content.split("|")]
                    is_sep = all(set(c.replace(" ", "")) <= {"-", ":"} and "-" in c for c in cells)
                    grid.append({"rendered": [_render_inline_markdown(c) for c in cells] if not is_sep else [], "is_sep": is_sep})
                cols = max(len(r["rendered"]) for r in grid if not r["is_sep"])
                widths = [0] * cols
                for r in grid:
                    if r["is_sep"]: continue
                    for c_idx, cell in enumerate(r["rendered"]): widths[c_idx] = max(widths[c_idx], _visible_len(cell))
                total_w = sum(widths) + (cols * 3) + 1
                if total_w > term_w:
                    shrink = (term_w - 10) / total_w
                    widths = [max(10, int(w * shrink)) for w in widths]
                def get_sep(l, m, r): return _ansi_wrap(l + m.join("─" * (w+2) for w in widths) + r, "36")
                lines.append(get_sep("┌", "┬", "┐"))
                v_bar = _ansi_wrap("│", "36")
                for r_idx, r in enumerate(grid):
                    if r["is_sep"]: lines.append(get_sep("├", "┼", "┤")); continue
                    wrapped = [_wrap_visible(r["rendered"][c_idx] if c_idx < len(r["rendered"]) else "", widths[c_idx]) for c_idx in range(cols)]
                    h = max(len(c) for c in wrapped)
                    for s in range(h):
                        parts = []
                        for c_idx in range(cols):
                            cell_l = wrapped[c_idx][s] if s < len(wrapped[c_idx]) else ""
                            parts.append(f" {cell_l}{' '*(widths[c_idx]-_visible_len(cell_l))} ")
                        lines.append(f"{v_bar}{v_bar.join(parts)}{v_bar}")
                    if r_idx < len(grid)-1 and not grid[r_idx+1]["is_sep"]: lines.append(get_sep("├", "┼", "┤"))
                lines.append(get_sep("└", "┴", "┘")); continue
            else: line = rows[0]; stripped = line.strip()
        if not stripped: lines.append("")
        elif stripped.startswith("#"):
            m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if m:
                lv = len(m.group(1)); color = "1;35" if lv <= 2 else ("1;36" if lv == 3 else "1")
                lines.append(_ansi_wrap(_render_inline_markdown(m.group(2)), color))
            else: lines.append(_render_inline_markdown(line))
        elif re.match(r"^\s*[-*+]\s+", line): lines.append(f"• {_render_inline_markdown(stripped.lstrip('-*+ '))}")
        elif re.match(r"^\s*\d+\.\s+", line): lines.append(_render_inline_markdown(line))
        elif stripped.startswith(">"): lines.append(f"{_ansi_wrap('> ', '90')}{_render_inline_markdown(stripped[1:].strip())}")
        elif re.match(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", stripped): lines.append(_ansi_wrap("─" * 32, "90"))
        else: lines.append(_render_inline_markdown(line))
        idx += 1
    return "\n".join(lines).strip()

# --- OPENROUTER CLIENT ---

class OpenRouterClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key; self.model = model
    def generate(self, messages: List[Dict[str, Any]], system: Optional[str] = None, tools: Optional[List[Dict[str, Any]]] = None, temp: float = 0.2) -> Dict[str, Any]:
        url = "https://openrouter.ai/api/v1/chat/completions"
        history = [{"role": "system", "content": system}] if system else []
        history.extend(messages)
        payload = {"model": self.model, "messages": history, "temperature": temp}
        if tools: payload["tools"] = tools; payload["tool_choice"] = "auto"
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST", headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/openrouter-cli", "X-Title": "OpenRouter CLI"
        })
        try:
            with urllib.request.urlopen(req, timeout=90) as resp: return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try: msg = json.loads(raw).get("error", {}).get("message", raw)
            except: msg = raw
            raise RuntimeError(f"OpenRouter Error: {msg}") from exc
    def list_models(self) -> List[Dict[str, Any]]:
        url = "https://openrouter.ai/api/v1/models"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.api_key}"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp: return json.loads(resp.read().decode()).get("data", [])
        except Exception as e:
            raise RuntimeError(f"Could not load models: {e}")

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
    if name == "fuzzy_apply_patch": return apply_fuzzy_unified_patch(str(args.get("patch", "")), cwd)
    if name == "request_follow_up": return f"Turn granted: {args.get('reason')}"
    return f"Unknown tool: {name}"

# --- STORAGE & TUI ---

def _require_api_crypto():
    if not all([AES, PBKDF2, get_random_bytes]):
        raise RuntimeError("pycryptodome required.")

def _encrypt_api_accounts(accs: Dict[str, str], pwd: str, tav: Optional[Dict[str, str]] = None) -> bytes:
    _require_api_crypto()
    payload = json.dumps({"accounts": accs, "tavily_accounts": tav or {}}, indent=2).encode()
    salt = get_random_bytes(16)
    key = PBKDF2(pwd.encode(), salt, dkLen=32, count=200_000)
    cipher = AES.new(key, AES.MODE_EAX)
    ct, tag = cipher.encrypt_and_digest(payload)
    
    def pk(part):
        return len(part).to_bytes(4, 'big') + part
        
    return API_ACCOUNTS_MAGIC + pk(salt) + pk(cipher.nonce) + pk(tag) + pk(ct)

def _decrypt_api_accounts(blob: bytes, pwd: str) -> Dict[str, Any]:
    _require_api_crypto()
    if not blob.startswith(API_ACCOUNTS_MAGIC):
        raise ValueError("Invalid lock file.")
        
    def upk(b, o):
        s = int.from_bytes(b[o:o+4], 'big')
        return b[o+4:o+4+s], o+4+s
        
    offset = len(API_ACCOUNTS_MAGIC)
    salt, offset = upk(blob, offset)
    nonce, offset = upk(blob, offset)
    tag, offset = upk(blob, offset)
    ciphertext, offset = upk(blob, offset)
    
    key = PBKDF2(pwd.encode(), salt, dkLen=32, count=200_000)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = json.loads(cipher.decrypt_and_verify(ciphertext, tag).decode())
    
    if not isinstance(data, dict):
        data = {"accounts": {}}
    if "accounts" not in data:
        data = {"accounts": data, "tavily_accounts": {}}
    if "tavily_accounts" not in data:
        data["tavily_accounts"] = {}
    return data

def classify_test_speed(elapsed_seconds: float) -> str:
    if elapsed_seconds <= 0.5: return "fast"
    if 3.0 <= elapsed_seconds <= 5.0: return "medium"
    if elapsed_seconds > 6.0: return "slow"
    return "normal"

def test_model(client: OpenRouterClient, model_id: str) -> str:
    test_client = OpenRouterClient(client.api_key, model_id)
    try:
        resp = test_client.generate([{"role": "user", "content": "Say exactly: OK"}], system="Reply OK only.", temp=0.0)
        content = resp["choices"][0]["message"]["content"]
        return _clean_response_text(content)
    except Exception as e: return f"Error: {e}"



    _require_api_crypto()
    if not blob.startswith(API_ACCOUNTS_MAGIC):
        raise ValueError("Invalid lock file.")
        
    def upk(b, o):
        s = int.from_bytes(b[o:o+4], 'big')
        return b[o+4:o+4+s], o+4+s
        
    offset = len(API_ACCOUNTS_MAGIC)
    salt, offset = upk(blob, offset)
    nonce, offset = upk(blob, offset)
    tag, offset = upk(blob, offset)
    ciphertext, offset = upk(blob, offset)
    
    key = PBKDF2(pwd.encode(), salt, dkLen=32, count=200_000)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    data = json.loads(cipher.decrypt_and_verify(ciphertext, tag).decode())
    
    if not isinstance(data, dict):
        data = {"accounts": {}}
    if "accounts" not in data:
        data = {"accounts": data, "tavily_accounts": {}}
    if "tavily_accounts" not in data:
        data["tavily_accounts"] = {}
    return data

def model_name(m: Dict[str, Any]) -> str: return str(m.get("id", ""))
def short_model_name(m: Dict[str, Any]) -> str:
    n = model_name(m); s = n.split("/")[-1] if "/" in n else n
    for p in ("llama-", "llama3-", "mixtral-", "gemma-", "gemini-"):
        if s.lower().startswith(p): s = s[len(p):]; break
    return s.replace("-", " ")

def build_model_table_widths(models: List[Dict[str, Any]]) -> Dict[str, int]:
    sw=0; nw=0; tw=0; stw=0
    for m in models:
        sw = max(sw, len(short_model_name(m))); nw = max(nw, len(model_name(m)))
        tw = max(tw, len(str(m.get("_tag") or ""))); stw = max(stw, len(str(m.get("_state") or "")))
    return {"short": min(max(sw, 15), 30), "name": min(max(nw, 20), 45), "tag": min(max(tw, 4), 10), "state": min(max(stw, 6), 16)}

def build_model_table_header(w: Dict[str, int]) -> List[str]:
    return [f"  {'Id':>2}  {'Model':<{w['short']}}  {'Full Name':<{w['name']}}  {'Uses':>4}  {'Tag':<{w['tag']}}  Cur  {'State':<{w['state']}}",
            f"  {'--':>2}  {'-'*w['short']}  {'-'*w['name']}  {'----'}  {'-'*w['tag']}  ---  {'-'*w['state']}"]

def format_model_entry(idx: int, m: Dict[str, Any], cur: str, w: Dict[str, int], sel: bool = False) -> str:
    n = model_name(m); dn = short_model_name(m); active = "*" if n == cur else " "; tag = str(m.get("_tag") or ""); usage = int(m.get("_uses") or 0); st = str(m.get("_state") or "")
    if st.startswith("cooldown"): st = _ansi_wrap(st, "31")
    marker = ">" if sel else " "; row = f"{marker} {idx:>2}  {dn[:w['short']]:<{w['short']}}  {n[:w['name']]:<{w['name']}}  {usage:>4}  {tag:<{w['tag']}}  {active}  {st:<{w['state']}}".rstrip()
    if sel: return _ansi_wrap(row, "48;5;24;97")
    if n == cur: return _ansi_wrap(row, "32")
    if m.get("_hidden"): return _ansi_wrap(row, "2")
    return row

def pick_api_account_interactive(accs: Dict[str, str], tav: Dict[str, str], cur: str) -> Optional[Dict[str, str]]:
    items = [{"action": "add", "provider": "openrouter", "name": "Add OpenRouter API", "masked_key": "", "state": "new"},
             {"action": "add", "provider": "tavily", "name": "Add Tavily API", "masked_key": "", "state": "new"}]
    for n, k in sorted(accs.items()): items.append({"action": "load", "provider": "openrouter", "name": n, "masked_key": f"{k[:4]}...{k[-4:]}", "state": "active" if n == cur else "saved"})
    for n, k in sorted(tav.items()): items.append({"action": "load", "provider": "tavily", "name": n, "masked_key": f"{k[:4]}...{k[-4:]}", "state": "saved"})
    pw = 0; nw = 0; kw = 0
    for it in items: pw = max(pw, len(it["provider"])); nw = max(nw, len(it["name"])); kw = max(kw, len(it["masked_key"]))
    w = {"prov": min(max(pw, 6), 10), "name": min(max(nw, 10), 28), "key": min(max(kw, 10), 24)}
    def render(it, i, sel):
        m = ">" if sel else " "
        row = f"{m} {i+1:>2}  {it['provider']:<{w['prov']}}  {it['name']:<{w['name']}}  {it['masked_key']:<{w['key']}}  {it['state']}"
        return _ansi_wrap(row, "48;5;24;97") if sel else (_ansi_wrap(row, "32") if it["action"]=="add" else row)
    return interactive_select("Manage API Accounts", items, render)

def pick_failover_interactive(proj: Optional[bool], sess: Optional[bool], glob: bool) -> Optional[Dict[str, str]]:
    items = [{"kind": "project", "scope": "Current project", "state": "inherit" if proj is None else ("on" if proj else "off"), "description": "Persistent override for project."},
             {"kind": "session", "scope": "This session", "state": "none" if sess is None else ("on" if sess else "off"), "description": "Temporary override for CLI lifetime."},
             {"kind": "default", "scope": "Global default", "state": "on" if glob else "off", "description": "Fallback when no project override exists."}]
    w = {"scope": 15, "state": 8, "description": 40}
    def render(it, i, sel):
        m = ">" if sel else " "; s = it["state"]; st = _ansi_wrap(s, "32" if s=="on" else ("31" if s=="off" else "33"))
        row = f"{m} {i+1:>2}  {it['scope']:<{w['scope']}}  {st:<{w['state']}}  {it['description']}"
        return _ansi_wrap(row, "48;5;24;97") if sel else row
    curr = 0
    while True:
        clear_screen(); title("Auto Failover")
        print("Use Up/Down, Space to toggle, Enter to close, Esc to cancel.\n")
        print(f"  {'Id':>2}  {'Scope':<15}  {'State':<8}  Description")
        for i, it in enumerate(items): print(render(it, i, i == curr))
        k = read_key()
        if k in ("\r", "\n"): return {it["kind"]: it["state"] for it in items}
        if k == "\x1b": return None
        if k == " ": items[curr]["state"] = "on" if items[curr]["state"] != "on" else "off"
        if k in ("\xe0H", "\x00H"): curr = (curr - 1) % len(items)
        elif k in ("\xe0P", "\x00P"): curr = (curr + 1) % len(items)

def read_key() -> str:
    if msvcrt is None: return input().strip()
    try:
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"): return ch + msvcrt.getwch()
        return ch
    except: return ""

def clear_screen():
    if sys.stdout.isatty(): os.system("cls" if os.name == "nt" else "clear")

def interactive_select(title_text: str, items: List[Any], render_item: Callable) -> Optional[Any]:
    if not items: return None
    idx = 0
    while True:
        clear_screen(); title(title_text); print("Use Up/Down, Enter to select, Esc to cancel.\n")
        for i, it in enumerate(items): print(render_item(it, i, i == idx))
        k = read_key()
        if k in ("\r", "\n"): return items[idx]
        if k == "\x1b": return None
        if k in ("\xe0H", "\x00H"): idx = (idx - 1) % len(items)
        elif k in ("\xe0P", "\x00P"): idx = (idx + 1) % len(items)

# --- AUTOCOMPLETE ---

if Completer is not None:
    class ORCliCompleter(Completer):
        SLASH_COMMANDS = [
            ("/help", "Show available commands"),
            ("/exit", "Quit CLI"),
            ("/reset", "Clear conversation history"),
            ("/mm", "Open model picker"),
            ("/test", "Test all models and hide failures"),
            ("/api", "Manage API accounts"),
            ("/failover", "Open auto-failover picker"),
            ("/tool", "Open tool manager"),
        ]
        def __init__(self, cwd): self.cwd = Path(cwd)
        def get_completions(self, document, complete_event):
            text = document.text_before_cursor
            if text.startswith("/"):
                if " " not in text:
                    for cmd, d in self.SLASH_COMMANDS:
                        if text.lower() in cmd.lower(): yield Completion(cmd, start_position=-len(text), display=cmd, display_meta=d)
            elif "@" in text:
                last_at = text.rfind("@"); after = text[last_at+1:]
                if " " not in after:
                    p = Path(after); dir_p = p.parent if "/" in after else Path("."); search = p.name if "/" in after else after
                    target = self.cwd / dir_p
                    if target.is_dir():
                        try:
                            for entry in target.iterdir():
                                if search.lower() in entry.name.lower():
                                    yield Completion(entry.name + ("/" if entry.is_dir() else ""), start_position=-len(search))
                        except: pass

# --- MAIN ---

def main():
    print("Starting OpenRouter CLI...")
    parser = argparse.ArgumentParser(); parser.add_argument("--api-key"); parser.add_argument("--password"); parser.add_argument("--model", default=None); args = parser.parse_args()
    
    prefs = {}
    if MODEL_PREFS_FILE.exists():
        try: prefs = json.loads(MODEL_PREFS_FILE.read_text(encoding="utf-8"))
        except: pass
    
    hidden = list(prefs.get("hidden_models", [])); speed = dict(prefs.get("speed_tags", {})); usage = dict(prefs.get("model_usage_counts", {}))
    dis_tools = set(prefs.get("disabled_tools", [])); last_m = str(prefs.get("last_model") or DEFAULT_MODEL); last_acc = str(prefs.get("last_api_account") or ""); sys_instr = str(prefs.get("system_instruction") or DEFAULT_SYSTEM)
    fail_u = int(prefs.get("failover_uses") or 0); af_glob = bool(prefs.get("auto_failover_default", False)); af_projs = dict(prefs.get("auto_failover_projects", {}))
    af_sess = None; cwd = Path.cwd()

    accs = {}; tav = {}
    if API_ACCOUNTS_FILE.exists():
        pwd = args.password or getpass.getpass("OpenRouter Lock Password: ")
        try: 
            dec = _decrypt_api_accounts(API_ACCOUNTS_FILE.read_bytes(), pwd)
            accs = dec["accounts"]; tav = dec["tavily_accounts"]
        except Exception as e:
            error(f"Failed to unlock: {e}")
            return 1
            
    api_k = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    act_acc = ""
    if not api_k and accs:
        act_acc = last_acc if last_acc in accs else next(iter(sorted(accs.keys(), key=str.lower)))
        api_k = accs[act_acc]
    
    if not api_k: api_k = "placeholder"
    
    client = OpenRouterClient(api_k, args.model or last_m); messages = []; model_cds = {}; history = []
    if PROMPT_HISTORY_FILE.exists():
        try:
            lines = PROMPT_HISTORY_FILE.read_text(encoding='utf-8', errors='replace').splitlines()
            seen = set(); history = []
            for l in reversed(lines):
                v = l.strip(); 
                if v and v not in seen: history.append(v); seen.add(v)
                if len(history) >= 200: break
            history.reverse()
        except: pass

    def persist():
        try:
            MODEL_PREFS_FILE.write_text(json.dumps({
                "hidden_models": sorted(set(hidden)), "speed_tags": speed, "model_usage_counts": usage, "disabled_tools": sorted(list(dis_tools)),
                "last_model": client.model, "last_api_account": act_acc, "system_instruction": sys_instr,
                "failover_uses": fail_u, "auto_failover_default": af_glob, "auto_failover_projects": af_projs
            }, indent=2), encoding="utf-8")
        except: pass
    
    def effective_af(): return af_sess if af_sess is not None else af_projs.get(str(cwd.resolve()), af_glob)
    def prune_cds():
        for n in [n for n, u in model_cds.items() if u <= _now()]: model_cds.pop(n, None); write_notification()

    clear_screen()
    title("OpenRouter Terminal CLI"); info(f"Project root: {cwd}")
    if api_k == "placeholder": warn("No API key found. Use /api to add one.")
    else: info(f"Model: {client.model}"); info(f"Auto failover: {'on' if effective_af() else 'off'}")

    while True:
        try:
            p_text = f"openrouter:{client.model.split('/')[-1] if '/' in client.model else client.model}"; prune_cds()
            if model_cds.get(client.model): p_text += f" [{format_cooldown_until(model_cds[client.model])}]"
            
            if pt_prompt:
                user_input = pt_prompt(ANSI(_ansi_wrap(f"{p_text}> ", "1;32")), history=InMemoryHistory(history), auto_suggest=AutoSuggestFromHistory(), completer=ORCliCompleter(cwd), complete_while_typing=True, complete_style=CompleteStyle.COLUMN, style=Style.from_dict({'': 'ansired'})).strip()
            else:
                user_input = input(_ansi_wrap(f"{p_text}> ", "1;32")).strip()
        except (EOFError, KeyboardInterrupt): print(); break
        
        if not user_input: user_input = "continue"; info("continue")
        if user_input in history: history.remove(user_input)
        history.append(user_input); 
        try: PROMPT_HISTORY_FILE.write_text("\n".join(history[-200:])+"\n", encoding='utf-8')
        except: pass
        
        if user_input.startswith("/"):
            ps = user_input.split(); cmd = ps[0].lower(); rem = " ".join(ps[1:])
            if cmd == "/exit" or cmd == "/quit": break
            if cmd == "/reset": messages = []; info("Reset."); continue
            if cmd == "/mm":
                try:
                    prune_cds(); 
                    if client.api_key == "placeholder": warn("Add an API key first via /api."); continue
                    raw = client.list_models()
                    
                    # Only show models that include ":free" in their ID
                    free_raw = [m for m in raw if ":free" in m.get('id', '')]
                    
                    decorated = []
                    for m in free_raw:
                        mid = m['id']; copy_m = dict(m)
                        copy_m["_tag"] = speed.get(mid, "")
                        copy_m["_uses"] = usage.get(mid, 0)
                        copy_m["_hidden"] = mid in hidden
                        cd = format_cooldown_until(model_cds.get(mid))
                        copy_m["_state"] = cd or ("hidden" if mid in hidden else "free")
                        decorated.append(copy_m)
                    
                    decorated.sort(key=lambda x: x['id'])

                    if rem:
                        target = rem.strip()
                        found_m = None
                        if target.isdigit():
                            idx = int(target)-1
                            if 0 <= idx < len(decorated): found_m = decorated[idx]['id']
                        else:
                            for m in decorated:
                                if target in m['id']: found_m = m['id']; break
                        if found_m:
                            client.model = found_m; info(f"Model: {client.model}"); persist()
                        else: warn("Model not found.")
                        continue

                    if rem:
                        target = rem.strip()
                        found_m = None
                        if target.isdigit():
                            idx = int(target)-1
                            if 0 <= idx < len(decorated): found_m = decorated[idx]['id']
                        else:
                            for m in decorated:
                                if target in m['id']: found_m = m['id']; break
                        if found_m:
                            client.model = found_m; info(f"Model: {client.model}"); persist()
                        else: warn("Model not found.")
                        continue

                    w = build_model_table_widths(decorated)
                    for l in build_model_table_header(w): print(l)
                    chosen = interactive_select("Select Model", decorated, lambda m, i, sel: format_model_entry(i+1, m, client.model, w, sel))
                    if chosen: client.model = chosen['id']; info(f"Model: {client.model}"); persist()
                except Exception as e: error(str(e))
                continue
            if cmd == "/test":
                if client.api_key == "placeholder": warn("Add an API key first."); continue
                info("Testing all models and auto-hiding failures...")
                try:
                    raw = client.list_models()
                    test_targets = [m for m in raw if ":free" in m['id']]
                    if not test_targets: test_targets = raw[:10]
                    
                    for m in test_targets:
                        mid = m['id']; print(f"- {mid} ... ", end="", flush=True)
                        start_t = time.perf_counter()
                        res = test_model(client, mid)
                        elapsed = time.perf_counter() - start_t
                        sp_tag = classify_test_speed(elapsed); speed[mid] = sp_tag
                        if res == "OK":
                            print(_ansi_wrap(f"OK [{sp_tag}] ({elapsed:.2f}s)", "32"))
                            if mid in hidden: hidden.remove(mid)
                        else:
                            print(_ansi_wrap(f"FAIL ({res})", "31"))
                            if mid not in hidden: hidden.append(mid)
                    persist(); info("Tests complete. Preferences updated.")
                except Exception as e: error(str(e))
                continue
            if cmd == "/api":
                chosen = pick_api_account_interactive(accs, tav, act_acc)
                if not chosen: continue
                p = chosen["provider"]
                if chosen["action"] == "add":
                    n = input(f"{p.title()} Name: ").strip(); k = input(f"{p.title()} Key: ").strip()
                    pwd = args.password or getpass.getpass("Lock Password: ")
                    if not pwd: error("Password required."); continue
                    if p == "tavily": tav[n] = k
                    else: accs[n] = k
                    try: 
                        API_ACCOUNTS_FILE.write_bytes(_encrypt_api_accounts(accs, pwd, tav))
                        if p == "openrouter": 
                            act_acc = n; client.api_key = k; persist()
                        info(f"Added {p} account: {n}")
                    except Exception as e: error(f"Failed: {e}")
                elif p == "openrouter": 
                    act_acc = chosen["name"]; api_k = accs[act_acc]; client.api_key = api_k; persist(); info(f"Switched: {act_acc}")
                continue
            if cmd == "/failover":
                c_af = pick_failover_interactive(af_projs.get(str(cwd.resolve())), af_sess, af_glob)
                if c_af:
                    if c_af["project"] == "inherit": af_projs.pop(str(cwd.resolve()), None)
                    else: af_projs[str(cwd.resolve())] = (c_af["project"] == "on")
                    af_sess = None if c_af["session"] == "none" else (c_af["session"] == "on")
                    af_glob = (c_af["default"] == "on"); persist(); info("Auto failover updated.")
                continue
            warn("Commands: /mm, /test, /api, /failover, /reset, /exit"); continue

        if client.api_key == "placeholder":
            warn("Please add an OpenRouter API key using /api first.")
            continue

        expanded = user_input
        if user_input.startswith("@"):
            h, _, t = user_input[1:].partition(" "); f_p = resolve_path(h, cwd); f_t = read_file(f_p); expanded = f"File: {f_p}\n\nContent:\n{f_t}\n\nUser: {t or 'Review the file.'}"
        messages.append({"role": "user", "content": expanded})
        failed_accs = set()
        for _ in range(DEFAULT_TOOL_LOOPS):
            try:
                cat = json.loads(TOOLS_FILE.read_text()) if TOOLS_FILE.exists() else []
                t_list = [t for t in cat if t['function']['name'] not in dis_tools]
                resp = client.generate(messages, system=sys_instr, tools=t_list)
                usage[client.model] = usage.get(client.model, 0) + 1; persist()
            except RuntimeError as exc:
                msg = str(exc); error(msg); is_rl = any(t in msg.lower() for t in ["rate limit", "429", "quota", "too many requests"])
                m = re.search(r"try again in ([0-9]+(?:\.[0-9]+)?)s", msg, re.I)
                if m: model_cds[client.model] = _now() + dt.timedelta(seconds=max(60.0, float(m.group(1)))); write_notification()
                if is_rl and effective_af() and len(accs) > 1:
                    failed_accs.add(act_acc); ord_a = sorted(accs.keys(), key=str.lower); start = ord_a.index(act_acc)+1 if act_acc in ord_a else 0
                    for cand in ord_a[start:] + ord_a[:start]:
                        if cand not in failed_accs: act_acc = cand; api_k = accs[cand]; client.api_key = api_k; fail_u += 1; persist(); info(f"Failover: {cand}"); break
                    else: break
                    continue
                break
            except Exception as e: error(str(e)); break
            msg_obj = resp["choices"][0]["message"]
            messages.append({"role": "assistant", "content": msg_obj.get("content")})
            if msg_obj.get("content"): print(f"\n{render_markdown_text(_clean_response_text(msg_obj['content']))}\n")
            if not msg_obj.get("tool_calls"): write_notification(); break
            for tc in msg_obj["tool_calls"]:
                t_n = tc["function"]["name"]; t_a = json.loads(tc["function"]["arguments"] or "{}")
                info(f"[tool] {t_n}"); res = execute_tool(t_n, t_a, cwd, tavily_accounts=tav)
                messages.append({"role": "tool", "tool_call_id": tc["id"], "content": res}); info(f"[result] {str(res)[:80]}...")
    return 0

if __name__ == "__main__": 
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
