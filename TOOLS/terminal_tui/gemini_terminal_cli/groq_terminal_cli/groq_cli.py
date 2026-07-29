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
    short_w = 0; name_w = 0; tag_w = 0
    for m in models:
        short_w = max(short_w, len(short_model_name(m)))
        name_w = max(name_w, len(model_name(m)))
        tag_w = max(tag_w, len(str(m.get("_tag") or "")))
    return {
        "short": min(max(short_w, 15), 30),
        "name": min(max(name_w, 20), 45),
        "tag": min(max(tag_w, 4), 10),
    }


def build_model_table_header(widths: Dict[str, int]) -> List[str]:
    return [
        f"  {'Id':>2}  {'Model':<{widths['short']}}  {'Full Name':<{widths['name']}}  {'Uses':>4}  {'Tag':<{widths['tag']}}  Cur",
        f"  {'--':>2}  {'-' * widths['short']}  {'-' * widths['name']}  {'-' * 4}  {'-' * widths['tag']}  ---",
    ]


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
        f"{active}"
    )
    
    if selected: return _ansi_wrap(row, "48;5;24;97")
    if name == current_model: return _ansi_wrap(row, "32")
    if model.get("_hidden"): return _ansi_wrap(row, "2")
    return row


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


def execute_tool(name: str, args: Dict[str, Any], cwd: Path) -> str:
    if name == "read_file": return read_file(resolve_path(args.get("filepath", ""), cwd))
    if name == "write_file": return write_file(resolve_path(args.get("filepath", ""), cwd), args.get("content", ""))
    if name == "list_directory": return list_directory(resolve_path(args.get("path", "."), cwd))
    if name == "get_system_info": return f"OS: {platform.system()} | CWD: {cwd}"
    if name == "search_file": return search_file(resolve_path(args.get("path", "."), cwd), str(args.get("query", "")), bool(args.get("recursive", False)))
    if name == "run_powershell": return run_powershell_command(str(args.get("command", "")), cwd, int(args.get("timeout_seconds", 60) or 60))
    if name == "smart_replace_block": return smart_replace_block_in_file(resolve_path(args.get("filepath", ""), cwd), str(args.get("old_text", "")), str(args.get("new_text", "")), int(args.get("occurrence", 1) or 1))
    if name == "replace_lines": return replace_lines_in_file(resolve_path(args.get("filepath", ""), cwd), int(args.get("start_line", 1)), int(args.get("end_line", 1)), str(args.get("new_text", "")))
    if name == "request_follow_up": return f"Turn granted: {args.get('reason')}"
    return f"Unknown tool: {name}"


def _require_api_crypto():
    if not all([AES, PBKDF2, get_random_bytes]): raise RuntimeError("pycryptodome required.")

def _encrypt_api_accounts(accounts: Dict[str, str], password: str) -> bytes:
    _require_api_crypto()
    payload = json.dumps({"accounts": accounts}, indent=2).encode("utf-8")
    salt = get_random_bytes(16)
    key = PBKDF2(password.encode(), salt, dkLen=32, count=200_000)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(payload)
    def pack(b): return len(b).to_bytes(4, 'big') + b
    return API_ACCOUNTS_MAGIC + pack(salt) + pack(cipher.nonce) + pack(tag) + pack(ciphertext)

def _decrypt_api_accounts(blob: bytes, password: str) -> Dict[str, str]:
    _require_api_crypto()
    if not blob.startswith(API_ACCOUNTS_MAGIC): raise ValueError("Invalid lock file.")
    def unpack(b, o):
        s = int.from_bytes(b[o:o+4], 'big')
        return b[o+4:o+4+s], o+4+s
    o = len(API_ACCOUNTS_MAGIC)
    salt, o = unpack(blob, o); nonce, o = unpack(blob, o); tag, o = unpack(blob, o); ct, o = unpack(blob, o)
    key = PBKDF2(password.encode(), salt, dkLen=32, count=200_000)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return json.loads(cipher.decrypt_and_verify(ct, tag).decode())["accounts"]


def test_model(client: GroqClient, model_id: str) -> str:
    test_client = GroqClient(client.api_key, model_id)
    try:
        resp = test_client.generate([{"role": "user", "content": "Say exactly: OK"}], system_instruction="Reply OK only.", temperature=0.0)
        return resp["choices"][0]["message"]["content"].strip()
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
    last_model = str(prefs.get("last_model") or DEFAULT_MODEL)
    system_instruction = str(prefs.get("system_instruction") or DEFAULT_SYSTEM)

    api_accounts = {}
    if API_ACCOUNTS_FILE.exists():
        pwd = args.password or getpass.getpass("Groq Lock Password: ")
        try: api_accounts = _decrypt_api_accounts(API_ACCOUNTS_FILE.read_bytes(), pwd)
        except: error("Failed to unlock API accounts."); return 1

    api_key = args.api_key or (next(iter(api_accounts.values())) if api_accounts else os.environ.get("GROQ_API_KEY"))
    if not api_key:
        error("No API key found. Start with --api-key or use /api.")
        api_key = "placeholder"

    active_model = args.model or last_model
    client = GroqClient(api_key, active_model)
    messages: List[Dict[str, Any]] = []
    cwd = Path.cwd()
    tools = json.loads(TOOLS_FILE.read_text(encoding="utf-8")) if TOOLS_FILE.exists() else None
    history = load_prompt_history()

    def persist_selection():
        payload = {
            "hidden_models": sorted(set(hidden_models)),
            "speed_tags": speed_tags,
            "model_usage_counts": model_usage_counts,
            "last_model": client.model,
            "system_instruction": system_instruction,
        }
        MODEL_PREFS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def record_usage(m_id: str):
        model_usage_counts[m_id] = model_usage_counts.get(m_id, 0) + 1
        persist_selection()

    title("Groq Terminal CLI (Fully Functional Port)")
    info(f"Model: {client.model} | Root: {cwd}")

    def get_prompt():
        return _ansi_wrap(f"groq:{client.model.split('-')[0]}> ", "1;32")

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
                    raw_models = client.list_models()
                    # Filter and decorate
                    decorated = []
                    for m in raw_models:
                        m_id = m['id']
                        copy_m = dict(m)
                        copy_m["_tag"] = speed_tags.get(m_id, "")
                        copy_m["_uses"] = model_usage_counts.get(m_id, 0)
                        copy_m["_hidden"] = m_id in hidden_models
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
                name = input("Account Name: "); key = input("Key: ")
                if name and key:
                    api_accounts[name] = key
                    pwd = args.password or getpass.getpass("Password to protect API file: ")
                    API_ACCOUNTS_FILE.write_bytes(_encrypt_api_accounts(api_accounts, pwd))
                    client.api_key = key; info("Saved and switched.")
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
            
            warn(f"Commands: /mm, /test, /api, /system, /save, /load, /reset, /exit")
            continue

        expanded_input = expand_at_file_prompt(user_input, cwd)
        messages.append({"role": "user", "content": expanded_input})
        
        for _ in range(DEFAULT_TOOL_LOOPS):
            try:
                response = client.generate(messages, system_instruction=system_instruction, tools=tools)
                record_usage(client.model)
            except Exception as e: error(str(e)); break
                
            msg = response["choices"][0]["message"]
            messages.append(msg)
            if msg.get("content"): print(f"\n{msg['content']}\n")
            if not msg.get("tool_calls"): write_notification(); break
                
            for tool_call in msg["tool_calls"]:
                t_id = tool_call["id"]
                t_name = tool_call["function"]["name"]
                try: t_args = json.loads(tool_call["function"]["arguments"])
                except: t_args = {}
                
                info(f"[tool] {t_name}")
                result = execute_tool(t_name, t_args, cwd)
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
