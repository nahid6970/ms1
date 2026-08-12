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


DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TOOL_LOOPS = 8
MAX_TEXT_CHARS = 12000
DEFAULT_MODEL_LIST_LIMIT = 12
MODELS_PAGE_SIZE = 1000
MODEL_PREFS_FILE = Path(__file__).with_name("model_prefs.json")
TOOLS_FILE = Path(__file__).with_name("tools.json")
PROMPT_HISTORY_FILE = Path(__file__).with_name("prompt_history.txt")
API_ACCOUNTS_FILE = Path(__file__).with_name("api_accounts.lock")
API_ACCOUNTS_LEGACY_FILE = Path(__file__).with_name("api_accounts.json")
API_ACCOUNTS_MAGIC = b"GEMAPI1"
NOTIFICATION_FILE = Path(r"C:\Users\nahid\notification.txt")
TRANSCRIPTS_DIR = Path(__file__).parent / "transcripts"
MEMORY_DIR = Path(__file__).parent / "memory"
MAIN_MEMORY_FILE = MEMORY_DIR / "main.json"
SKILLS_DIR = Path(__file__).parent / "skills"

DEFAULT_SYSTEM = (
    "You are a terminal coding assistant. "
    "Be concise, practical, and ask before making destructive changes. "
    "For code work, inspect with run_powershell commands such as rg and Get-Content first. "
    "When using Select-String for literal code text, use -SimpleMatch and single-quoted patterns. "
    "Prefer apply_patch or smart_replace_block for edits only after refreshing the exact surrounding context. "
    "Always double-check your changes using verify_file_content or read_file after making modifications to confirm they were actually applied. "
    "AUTOSAVE MEMORY & USER BEHAVIOR: Memory tools are active. You MUST immediately call `save_memory` whenever the user shares personal facts or preferences. "
    f"CREATING SKILLS: When the user asks to create or add a skill, ALWAYS use write_file to save a markdown file into `{SKILLS_DIR.as_posix()}/<skill_name>.md` so it is loaded by /skill. DO NOT call save_memory for skills!"
)

try:
    import msvcrt
except Exception:
    msvcrt = None

try:
    from prompt_toolkit import prompt as pt_prompt
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.formatted_text import ANSI
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.lexers import Lexer
    from prompt_toolkit.shortcuts import CompleteStyle
    from prompt_toolkit.styles import Style
except Exception:
    pt_prompt = None
    AutoSuggestFromHistory = None
    Completer = None
    Completion = None
    ANSI = None
    FileHistory = None
    InMemoryHistory = None
    Lexer = None
    CompleteStyle = None
    Style = None


if Lexer is not None:
    class CustomUserTextLexer(Lexer):
        def lex_document(self, document):
            def get_line(lineno):
                return [("class:custom-user-text", document.lines[lineno])]
            return get_line
else:
    CustomUserTextLexer = None


def _now_stamp() -> str:
    # High resolution timestamp ensures notification daemon sees unique text on every call
    return dt.datetime.now().strftime("%Y-%m-%d-%H:%M:%S.%f")


def _now() -> dt.datetime:
    return dt.datetime.now()


def write_notification() -> None:
    try:
        NOTIFICATION_FILE.write_text(_now_stamp(), encoding="utf-8")
    except Exception:
        pass


def ensure_memory_dir() -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def load_main_memory() -> Dict[str, Any]:
    ensure_memory_dir()
    if not MAIN_MEMORY_FILE.exists():
        default_main = {
            "summary": "Main memory index and core basic memories",
            "basic_memories": {},
            "sub_memories": {},
        }
        try:
            MAIN_MEMORY_FILE.write_text(json.dumps(default_main, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        return default_main
    try:
        data = json.loads(MAIN_MEMORY_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"summary": "Main memory index", "basic_memories": {}, "sub_memories": {}}
        if "basic_memories" not in data or not isinstance(data.get("basic_memories"), dict):
            data["basic_memories"] = {}
        if "sub_memories" not in data or not isinstance(data.get("sub_memories"), dict):
            data["sub_memories"] = {}
        return data
    except Exception:
        return {"summary": "Main memory index", "basic_memories": {}, "sub_memories": {}}


def save_main_memory(data: Dict[str, Any]) -> None:
    ensure_memory_dir()
    try:
        MAIN_MEMORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def resolve_memory_path(raw_path: str) -> tuple[Path, str]:
    """Returns (target_file_path, format_type ['json' or 'md'])."""
    ensure_memory_dir()
    clean = raw_path.strip().replace("\\", "/").strip("/")
    if not clean or clean in {"main", "main.json", "."}:
        return MAIN_MEMORY_FILE, "json"

    fmt = "md" if clean.lower().endswith(".md") else "json"
    if not (clean.lower().endswith(".json") or clean.lower().endswith(".md")):
        clean += ".json"

    target = (MEMORY_DIR / clean).resolve()
    if not str(target).startswith(str(MEMORY_DIR.resolve())):
        return MAIN_MEMORY_FILE, "json"
    return target, fmt


def save_memory(key: str = "", content: str = "", path: str = "main", description: str = "") -> str:
    key = str(key or "").strip()
    content = str(content or "").strip()
    path_clean = str(path or "").strip().replace("\\", "/").lower()
    if path_clean.startswith("skills/") or path_clean == "skills" or key.lower().startswith("skill_") or key.lower() == "skill":
        return f"Error: Do NOT use save_memory for skills. Use `write_file` to write a Markdown file directly into `{SKILLS_DIR.as_posix()}/<skill_name>.md` so it is loaded by /skill."
    if not key and not content:
        return "Error: memory content or key is required."
    if not key:
        lower_c = content.lower()
        if any(w in lower_c for w in ("name", "my name")):
            key = "user_name"
        elif any(w in lower_c for w in ("don't", "do not", "never", "always", "prefer", "dislike", "like", "style", "behavior")):
            key = "user_behavior"
        else:
            key = "user_info"
    if not content:
        content = key

    target_file, fmt = resolve_memory_path(path)

    if target_file == MAIN_MEMORY_FILE.resolve():
        main_data = load_main_memory()
        main_data["basic_memories"][key] = {
            "content": content,
            "updated_at": _now_stamp(),
        }
        save_main_memory(main_data)
        return f"Successfully saved memory '{key}': '{content}' to main memory."

    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        rel_path = str(target_file.relative_to(MEMORY_DIR)).replace("\\", "/")

        if fmt == "md":
            existing_text = target_file.read_text(encoding="utf-8", errors="replace") if target_file.exists() else ""
            heading = f"## {key}\n" if key else ""
            entry_text = f"{heading}{content.strip()}\n"

            if existing_text and heading and heading in existing_text:
                parts = existing_text.split(heading)
                before = parts[0]
                after_parts = parts[1].split("\n## ", 1)
                after = f"\n## {after_parts[1]}" if len(after_parts) > 1 else ""
                new_text = f"{before}{heading}{content.strip()}\n{after}"
            elif existing_text:
                new_text = f"{existing_text.rstrip()}\n\n{entry_text}"
            else:
                new_text = f"# Memory Topic: {rel_path}\n\n{entry_text}"

            target_file.write_text(new_text, encoding="utf-8")
            item_count = new_text.count("\n## ") or 1
        else:
            sub_data = {}
            if target_file.exists():
                try:
                    sub_data = json.loads(target_file.read_text(encoding="utf-8"))
                except Exception:
                    sub_data = {}
            if not isinstance(sub_data, dict):
                sub_data = {}

            sub_data[key] = {
                "content": content,
                "updated_at": _now_stamp(),
            }
            target_file.write_text(json.dumps(sub_data, indent=2, ensure_ascii=False), encoding="utf-8")
            item_count = len(sub_data)

        main_data = load_main_memory()
        sub_desc = description.strip() if description else f"Sub-memory topic ({fmt.upper()}) for '{rel_path}'"
        main_data["sub_memories"][rel_path] = {
            "description": sub_desc,
            "updated_at": _now_stamp(),
            "items_count": item_count,
            "format": fmt,
        }
        save_main_memory(main_data)
        return f"Successfully saved memory '{key}' to '{rel_path}' ({fmt.upper()}) and updated main memory index."
    except Exception as exc:
        return f"Error saving memory to {path}: {exc}"


def read_memory(path: str = "main", key: Optional[str] = None) -> str:
    target_file, fmt = resolve_memory_path(path)

    if target_file == MAIN_MEMORY_FILE.resolve():
        main_data = load_main_memory()
        basic = main_data.get("basic_memories", {})
        sub_files = main_data.get("sub_memories", {})

        if key and key.strip():
            k = key.strip()
            if k in basic:
                item = basic[k]
                c = item.get("content", str(item)) if isinstance(item, dict) else str(item)
                return f"Main Memory Basic Item ['{k}']:\n{c}"
            for sub_p, sub_info in sub_files.items():
                if k.lower() in sub_p.lower():
                    desc = sub_info.get("description", "") if isinstance(sub_info, dict) else str(sub_info)
                    return f"Sub-memory match ['{sub_p}']:\nDescription: {desc}\nUse read_memory(path='{sub_p}') to read full memory file."
            return f"Key/Path '{k}' not found in main memory."

        lines = ["=== MAIN MEMORY ==="]
        if basic:
            lines.append("\n[Basic Core Memories]:")
            for bk, bv in sorted(basic.items()):
                c = bv.get("content", str(bv)) if isinstance(bv, dict) else str(bv)
                lines.append(f"  - {bk}: {c}")
        else:
            lines.append("\n[Basic Core Memories]: None saved yet.")

        if sub_files:
            lines.append("\n[Sub-Memory Index]:")
            for sp, sinfo in sorted(sub_files.items()):
                desc = sinfo.get("description", "") if isinstance(sinfo, dict) else str(sinfo)
                cnt = sinfo.get("items_count", "?") if isinstance(sinfo, dict) else "?"
                lines.append(f"  - {sp} ({cnt} items): {desc}")
        else:
            lines.append("\n[Sub-Memory Index]: None created yet.")

        return "\n".join(lines)

    if not target_file.exists():
        rel_p = str(target_file.relative_to(MEMORY_DIR)).replace("\\", "/")
        return f"Sub-memory file '{rel_p}' does not exist."

    try:
        rel_p = str(target_file.relative_to(MEMORY_DIR)).replace("\\", "/")
        if fmt == "md":
            content = target_file.read_text(encoding="utf-8", errors="replace")
            return f"=== SUB-MEMORY ({fmt.upper()}): {rel_p} ===\n\n{content}"

        sub_data = json.loads(target_file.read_text(encoding="utf-8"))
        if not isinstance(sub_data, dict) or not sub_data:
            return f"Sub-memory file '{rel_p}' is empty."

        if key and key.strip():
            k = key.strip()
            if k in sub_data:
                item = sub_data[k]
                c = item.get("content", str(item)) if isinstance(item, dict) else str(item)
                return f"Sub-memory '{rel_p}' ['{k}']:\n{c}"
            return f"Key '{k}' not found in sub-memory '{rel_p}'. Available keys: {', '.join(sub_data.keys())}"

        lines = [f"=== SUB-MEMORY ({fmt.upper()}): {rel_p} ({len(sub_data)} items) ==="]
        for sk, sv in sorted(sub_data.items()):
            c = sv.get("content", str(sv)) if isinstance(sv, dict) else str(sv)
            lines.append(f"\nKey: {sk}\nContent: {c}")
        return "\n".join(lines)
    except Exception as exc:
        return f"Error reading sub-memory file: {exc}"


def list_memories() -> str:
    ensure_memory_dir()
    main_data = load_main_memory()
    sub_files = main_data.get("sub_memories", {})

    lines = ["=== MEMORY DIRECTORY ===", f"Location: {MEMORY_DIR}"]
    lines.append(f"Main Memory File: main.json ({len(main_data.get('basic_memories', {}))} basic items)")

    physical_files = []
    for p in sorted(MEMORY_DIR.rglob("*")):
        if p.is_file() and p.name != "main.json" and p.suffix in {".json", ".md"}:
            rel_p = str(p.relative_to(MEMORY_DIR)).replace("\\", "/")
            physical_files.append(rel_p)

    if physical_files:
        lines.append("\nSub-memory Files & Folders:")
        for sp in physical_files:
            sinfo = sub_files.get(sp, {})
            desc = sinfo.get("description", "Unindexed memory file") if isinstance(sinfo, dict) else str(sinfo)
            fmt_str = "MD" if sp.endswith(".md") else "JSON"
            lines.append(f"  • {sp} [{fmt_str}] - {desc}")
    else:
        lines.append("\nNo sub-memory files created yet.")

    return "\n".join(lines)


def delete_memory_item(path: str = "main", key: Optional[str] = None) -> str:
    target_file, fmt = resolve_memory_path(path)

    if target_file == MAIN_MEMORY_FILE.resolve():
        main_data = load_main_memory()
        if key and key.strip():
            k = key.strip()
            if k in main_data.get("basic_memories", {}):
                del main_data["basic_memories"][k]
                save_main_memory(main_data)
                return f"Deleted basic memory item '{k}' from main memory."
            if k in main_data.get("sub_memories", {}):
                del main_data["sub_memories"][k]
                save_main_memory(main_data)
                return f"Removed sub-memory index entry '{k}' from main memory."
            return f"Key '{k}' not found in main memory."
        return "Error: key is required when deleting from main memory."

    if not target_file.exists():
        return f"Error: memory file '{path}' not found."

    rel_p = str(target_file.relative_to(MEMORY_DIR)).replace("\\", "/")

    if key and key.strip():
        k = key.strip()
        try:
            if fmt == "md":
                existing_text = target_file.read_text(encoding="utf-8", errors="replace")
                heading = f"## {k}\n"
                if heading in existing_text:
                    parts = existing_text.split(heading)
                    before = parts[0]
                    after_parts = parts[1].split("\n## ", 1)
                    after = f"\n## {after_parts[1]}" if len(after_parts) > 1 else ""
                    new_text = f"{before.strip()}\n{after.strip()}\n"
                    target_file.write_text(new_text.strip() + "\n", encoding="utf-8")
                    item_count = new_text.count("\n## ") or (1 if new_text.strip() else 0)
                else:
                    return f"Key/Heading '{k}' not found in sub-memory '{rel_p}'."
            else:
                sub_data = json.loads(target_file.read_text(encoding="utf-8"))
                if isinstance(sub_data, dict) and k in sub_data:
                    del sub_data[k]
                    target_file.write_text(json.dumps(sub_data, indent=2, ensure_ascii=False), encoding="utf-8")
                    item_count = len(sub_data)
                else:
                    return f"Key '{k}' not found in sub-memory '{rel_p}'."

            main_data = load_main_memory()
            if rel_p in main_data.get("sub_memories", {}):
                if item_count <= 0:
                    del main_data["sub_memories"][rel_p]
                else:
                    main_data["sub_memories"][rel_p]["items_count"] = item_count
                save_main_memory(main_data)
            return f"Deleted key '{k}' from sub-memory '{rel_p}'."
        except Exception as exc:
            return f"Error updating sub-memory file: {exc}"

    try:
        target_file.unlink()
        main_data = load_main_memory()
        if rel_p in main_data.get("sub_memories", {}):
            del main_data["sub_memories"][rel_p]
            save_main_memory(main_data)
        return f"Deleted sub-memory file '{rel_p}' and removed it from main memory index."
    except Exception as exc:
        return f"Error deleting file '{rel_p}': {exc}"


def get_effective_system_instruction(base_system: str, disabled_tools: Set[str]) -> str:
    if "read_memory" in disabled_tools:
        return base_system
    main_data = load_main_memory()
    basic = main_data.get("basic_memories", {})
    sub_files = main_data.get("sub_memories", {})

    if not basic and not sub_files:
        return base_system

    memory_lines = ["\n\n[Active Main Memory & Index]"]
    if basic:
        memory_lines.append("Basic Core Memories:")
        for k, v in sorted(basic.items()):
            c = v.get("content", str(v)) if isinstance(v, dict) else str(v)
            memory_lines.append(f"  - {k}: {c}")

    if sub_files:
        memory_lines.append("Sub-Memory Topics Index (use read_memory(path='<sub_path>') to view deep details):")
        for sp, sinfo in sorted(sub_files.items()):
            desc = sinfo.get("description", "") if isinstance(sinfo, dict) else str(sinfo)
            memory_lines.append(f"  - {sp}: {desc}")

    return base_system + "\n".join(memory_lines)




def _ansi_wrap(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def _char_width(char: str) -> int:
    """Returns terminal display width of a single character (1 for narrow, 2 for wide/emoji, 0 for zero-width)."""
    if not char:
        return 0
    cp = ord(char)
    if cp < 32 or (0x7F <= cp <= 0x9F) or unicodedata.category(char) in ("Mn", "Me", "Cf"):
        return 0
    eaw = unicodedata.east_asian_width(char)
    if eaw in ("W", "F"):
        return 2
    if (
        (0x1F300 <= cp <= 0x1F1FF) or
        (0x1F300 <= cp <= 0x1F5FF) or
        (0x1F600 <= cp <= 0x1F64F) or
        (0x1F680 <= cp <= 0x1F6FF) or
        (0x1F900 <= cp <= 0x1F9FF) or
        (0x1FA70 <= cp <= 0x1FAFF) or
        (0x2600 <= cp <= 0x27BF) or
        (0x2300 <= cp <= 0x23FF)
    ):
        return 2
    return 1


def _visible_len(text: str) -> int:
    """Calculate the visible terminal display width of a string, ignoring ANSI escape codes and accounting for emojis."""
    clean = re.sub(r'\x1b\[[0-9;?]*[a-zA-Z]', '', text)
    clean = clean.replace('\ufe0f', '').replace('\ufe0e', '')
    return sum(_char_width(c) for c in clean)


def _format_seconds(seconds: float) -> str:
    total = max(0, int(seconds + 0.999))
    minutes, secs = divmod(total, 60)
    return f"{minutes:02d}:{secs:02d}"


def _format_token_count(num_tokens: int) -> str:
    if num_tokens >= 1_000_000:
        return f"{num_tokens / 1_000_000:.1f}M"
    if num_tokens >= 1_000:
        return f"{num_tokens / 1_000:.1f}k"
    return str(num_tokens)



def info(text: str) -> None:
    print(_ansi_wrap(text, "36"))


def warn(text: str) -> None:
    print(_ansi_wrap(text, "33"))


def error(text: str) -> None:
    print(_ansi_wrap(text, "31"))


def load_prompt_history(max_items: int = 200) -> List[str]:
    """Load history, deduplicating globally and stripping legacy prefixes."""
    try:
        if not PROMPT_HISTORY_FILE.exists():
            return []
        
        raw_lines = PROMPT_HISTORY_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
        items: List[str] = []
        seen = set()
        
        # Process from newest to oldest to preserve most recent entries
        for line in reversed(raw_lines):
            value = line.strip()
            # Clean legacy prefixes if they exist (e.g. from external logs)
            if value.startswith('+'):
                value = value[1:].strip()
            # Skip comments and empty lines
            if not value or value.startswith('#'):
                continue
                
            if value not in seen:
                items.append(value)
                seen.add(value)
            if len(items) >= max_items:
                break
        
        return list(reversed(items))
    except Exception:
        return []


def append_prompt_history(user_input: str, memory_history: List[str], max_items: int = 200) -> None:
    """Add item to history, moving it to the end if it already exists, and sync to file."""
    value = user_input.strip()
    if not value:
        return
        
    # Global deduplication: remove existing instances to move this command to the end
    if value in memory_history:
        memory_history[:] = [item for item in memory_history if item != value]
        
    memory_history.append(value)
    if len(memory_history) > max_items:
        del memory_history[:-max_items]
        
    try:
        # Overwrite file to maintain a deduplicated and cleaned state
        PROMPT_HISTORY_FILE.write_text("\n".join(memory_history) + "\n", encoding="utf-8")
    except Exception:
        pass


if Completer is not None:
    class GeminiCliCompleter(Completer):
        SLASH_COMMANDS = [
            ("/help", "Show available commands"),
            ("/exit", "Quit CLI"),
            ("/quit", "Quit CLI"),
            ("/reset", "Clear conversation history"),
            ("/mm", "Open model picker / switch model"),
            ("/test", "Test all models and hide failures"),
            ("/api", "Open API account picker"),
            ("/settings", "Open interactive CLI settings"),
            ("/loops", "Set max tool-call loops"),
            ("/failover", "Open auto-failover picker"),
            ("/tool", "Open tool manager"),
            ("/system", "Replace or load system instruction"),
            ("/skill", "Browse and apply saved skill instructions"),
            ("/resume", "Resume a recent conversation session"),
            ("/r", "Resume a recent conversation session"),
            ("/save", "Save transcript JSON"),
            ("/load", "Load transcript JSON"),
            ("/tokens", "Show estimated conversation token usage"),
            ("/run", "Execute code blocks from the last AI response"),
            ("/alias", "Manage custom prompt macros"),
        ]


        def _get_skill_completions(self, search_part: str) -> List[tuple[str, str, str]]:
            skills = list_skills(cwd=self.cwd)
            results = []
            for title_str, desc_str, path in skills:
                name = path.stem
                if not search_part or search_part.lower() in name.lower() or search_part.lower() in title_str.lower():
                    results.append((name, name, title_str))
            return results

        def _get_alias_completions(self, aliases: Dict[str, str], search_part: str) -> List[tuple[str, str, str]]:
            results = []
            for name, prompt in sorted(aliases.items()):
                if not search_part or search_part.lower() in name.lower() or search_part.lower() in prompt.lower():
                    results.append((name, name, prompt[:40]))
            return results

        def __init__(self, cwd: Optional[Path] = None):
            self.cwd = Path(cwd) if cwd else Path.cwd()

        def _get_path_completions(self, raw_path: str) -> List[tuple[str, str, str]]:
            raw_path = raw_path.replace("\\", "/")
            if "/" in raw_path:
                dir_part, _, search_part = raw_path.rpartition("/")
            else:
                dir_part, search_part = "", raw_path

            if dir_part:
                if dir_part == "~" or dir_part.startswith("~/"):
                    target_dir = Path(dir_part).expanduser()
                else:
                    target_dir = self.cwd / dir_part
            else:
                target_dir = self.cwd

            if not target_dir.exists() or not target_dir.is_dir():
                return []

            results: List[tuple[str, str, str]] = []
            search_lower = search_part.lower()
            try:
                for entry in sorted(target_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
                    name = entry.name
                    if name.startswith(".") and not search_lower.startswith("."):
                        continue
                    if name == "__pycache__" and not search_lower.startswith("__"):
                        continue
                    
                    name_lower = name.lower()
                    # Match if substring is anywhere or matches subsequence (e.g. "ss" matches "RcloneSS")
                    matched = False
                    if not search_lower or search_lower in name_lower:
                        matched = True
                    else:
                        # Subsequence match check
                        s_idx = 0
                        for char in name_lower:
                            if s_idx < len(search_lower) and char == search_lower[s_idx]:
                                s_idx += 1
                        if s_idx == len(search_lower):
                            matched = True

                    if matched:
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
                    if cmd_lower in {"/save", "/load", "/system", "/resume", "/r"}:
                        for full_rel, display_name, meta in self._get_path_completions(arg_part):
                            yield Completion(
                                full_rel,
                                start_position=-len(arg_part),
                                display=display_name,
                                display_meta=meta,
                            )
                        return
                    if cmd_lower == "/skill":
                        for full_rel, display_name, meta in self._get_skill_completions(arg_part):
                            yield Completion(
                                full_rel,
                                start_position=-len(arg_part),
                                display=display_name,
                                display_meta=meta,
                            )
                        return
                    if cmd_lower == "/alias":
                        # Suggest existing aliases or subcommands
                        sub_choices = [("list", "List all aliases"), ("add", "Add alias"), ("remove", "Remove alias")]
                        for sc, desc in sub_choices:
                            if not arg_part or arg_part.lower() in sc:
                                yield Completion(sc, start_position=-len(arg_part), display=sc, display_meta=desc)
                        # Also suggest alias names for running
                        for full_rel, display_name, meta in self._get_alias_completions(load_model_prefs().get("aliases", {}), arg_part):
                            yield Completion(full_rel, start_position=-len(arg_part), display=display_name, display_meta=meta)
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
    GeminiCliCompleter = None


def read_dynamic_prompt(
    prompt_provider: Callable[[], str],
    history: Optional[List[str]] = None,
    cwd: Optional[Path] = None,
    prompt_fg: str = "ansired",
    prompt_bg: str = "",
) -> str:
    """Read a line while allowing a time-sensitive prompt to refresh."""
    if pt_prompt is not None and ANSI is not None and InMemoryHistory is not None and CompleteStyle is not None and Style is not None:
        prompt_history = InMemoryHistory(history or [])
        completer = GeminiCliCompleter(cwd=cwd) if GeminiCliCompleter is not None else None
        
        bg_str = prompt_bg.strip()
        fg_str = prompt_fg.strip() or "ansired"
        if bg_str and bg_str != "none":
            if not bg_str.startswith("bg:"):
                bg_str = f"bg:{bg_str}"
            text_style_spec = f"{bg_str} {fg_str}"
        else:
            text_style_spec = fg_str

        user_style = Style.from_dict({
            'custom-user-text': text_style_spec,
            '': fg_str,
            # Sleek dark-mode completion popup theme
            'completion-menu': 'bg:#181825 #cdd6f4',
            'completion-menu.completion': 'bg:#181825 #89dceb',
            'completion-menu.completion.current': 'bg:#005f87 #ffffff bold',
            'completion-menu.meta.completion': 'bg:#181825 #9399b2',
            'completion-menu.meta.completion.current': 'bg:#005f87 #e0e0e0',
            'scrollbar.background': 'bg:#11111b',
            'scrollbar.button': 'bg:#313244',
        })

        lexer = CustomUserTextLexer() if CustomUserTextLexer is not None else None
        
        return pt_prompt(
            message=lambda: ANSI(prompt_provider()),
            history=prompt_history,
            auto_suggest=AutoSuggestFromHistory() if AutoSuggestFromHistory is not None else None,
            completer=completer,
            lexer=lexer,
            complete_while_typing=True,
            complete_style=CompleteStyle.COLUMN,
            mouse_support=False,
            wrap_lines=True,
            refresh_interval=0.25,
            style=user_style,
        )

    return input(prompt_provider())


def title(text: str) -> None:
    print(_ansi_wrap(text, "1;35"))


def resolve_path(raw: str, cwd: Path) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = cwd / candidate
    return candidate.resolve()


def read_file(path: Path) -> str:
    if not path.exists():
        return f"Error: file not found: {path}"
    if path.is_dir():
        return f"Error: {path} is a directory."
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        if len(content) > MAX_TEXT_CHARS:
            return content[:MAX_TEXT_CHARS] + "\n\n... (truncated)"
        return content
    except Exception as exc:
        return f"Error reading file: {exc}"


def write_file(path: Path, content: str) -> str:
    try:
        if path.parent:
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to {path}"
    except Exception as exc:
        return f"Error writing file: {exc}"


def replace_file(path: Path, content: str) -> str:
    return write_file(path, content)


def delete_path(path: Path) -> str:
    try:
        if not path.exists():
            return f"Error: path not found: {path}"
        if path.is_dir():
            import shutil

            shutil.rmtree(path)
            return f"Deleted directory: {path}"
        path.unlink()
        return f"Deleted file: {path}"
    except Exception as exc:
        return f"Error deleting path: {exc}"


def search_file(path: Path, query: str, recursive: bool = False, max_results: int = 20) -> str:
    if not query.strip():
        return "Error: query is required."
    if not path.exists():
        return f"Error: path not found: {path}"

    results: List[str] = []
    query_lower = query.lower()

    def scan_file(file_path: Path) -> None:
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return
        for lineno, line in enumerate(text.splitlines(), start=1):
            if query_lower in line.lower():
                results.append(f"{file_path}:{lineno}: {line}")
                if len(results) >= max_results:
                    return

    if path.is_file():
        scan_file(path)
    else:
        for file_path in sorted(path.rglob("*")) if recursive else sorted(path.iterdir()):
            if len(results) >= max_results:
                break
            if file_path.is_file():
                scan_file(file_path)

    return "\n".join(results) if results else "No matches."


def search_web(query: str, max_results: int = 5) -> str:
    if not query.strip():
        return "Error: query is required."
    max_results = max(1, min(int(max_results or 5), 10))
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return f"Error searching web: {exc}"

    results: List[str] = []
    pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(raw):
        href = html.unescape(match.group("href"))
        title = re.sub(r"<[^>]+>", "", match.group("title"))
        title = html.unescape(title).strip()
        parsed = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed.query)
        if "uddg" in params:
            href = params["uddg"][0]
        if title and href:
            results.append(f"{len(results) + 1}. {title}\n   {href}")
        if len(results) >= max_results:
            break
    return "\n".join(results) if results else "No web results found."


def inspect_image_file(filepath: Path) -> tuple[str, Optional[Dict[str, Any]]]:
    """Inspects an image file and returns metadata and inlineData dict for Gemini multimodal vision."""
    if not filepath.exists():
        return f"Error: file not found: {filepath}", None
    if filepath.is_dir():
        return f"Error: {filepath} is a directory.", None

    ext = filepath.suffix.lower()
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
    }
    mime_type = mime_types.get(ext, "image/png")

    try:
        data = filepath.read_bytes()
        import base64
        b64_str = base64.b64encode(data).decode("utf-8")
        
        info_str = f"Loaded image '{filepath.name}' ({len(data) / 1024:.1f} KB, {mime_type})."
        
        try:
            from PIL import Image
            import io
            with Image.open(io.BytesIO(data)) as img:
                info_str += f" Resolution: {img.width}x{img.height}, Mode: {img.mode}."
        except Exception:
            pass

        inline_part = {
            "inlineData": {
                "mimeType": mime_type,
                "data": b64_str
            }
        }
        return info_str, inline_part
    except Exception as exc:
        return f"Error inspecting image: {exc}", None


def search_tavily(query: str, tavily_accounts: Dict[str, str], max_results: int = 5) -> str:
    if not query.strip():
        return "Error: query is required."
    if not tavily_accounts:
        return "Error: no Tavily API accounts saved. Use /api to add one."
    max_results = max(1, min(int(max_results or 5), 10))
    errors: List[str] = []
    for account_name, api_key in sorted(tavily_accounts.items(), key=lambda item: item[0].lower()):
        payload = {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        request = urllib.request.Request(
            "https://api.tavily.com/search",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read().decode("utf-8", errors="replace")
                body = json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            errors.append(f"{account_name}: HTTP {exc.code} {raw[:160]}")
            if exc.code in {401, 402, 403, 429}:
                continue
            continue
        except Exception as exc:
            errors.append(f"{account_name}: {exc}")
            continue

        results = body.get("results", [])
        if not isinstance(results, list):
            results = []
        lines = [f"Tavily account: {account_name}"]
        for idx, result in enumerate(results[:max_results], start=1):
            if not isinstance(result, dict):
                continue
            title = str(result.get("title") or "Untitled").strip()
            url = str(result.get("url") or "").strip()
            content = str(result.get("content") or "").strip()
            lines.append(f"{idx}. {title}\n   {url}\n   {content}".rstrip())
        return "\n".join(lines) if len(lines) > 1 else f"Tavily account: {account_name}\nNo results."
    return "Error: all Tavily API accounts failed.\n" + "\n".join(errors)


def _replace_nth(text: str, old: str, new: str, occurrence: int = 1) -> tuple[str, bool]:
    if occurrence < 1:
        occurrence = 1
    idx = -1
    start = 0
    for _ in range(occurrence):
        idx = text.find(old, start)
        if idx < 0:
            return text, False
        start = idx + len(old)
    return text[:idx] + new + text[idx + len(old):], True


def replace_block_in_file(path: Path, old_text: str, new_text: str, occurrence: int = 1) -> str:
    if not path.exists():
        return f"Error: path not found: {path}"
    # Prevent infinite loop when AI attempts no-op replacement where old_text == new_text
    if old_text == new_text:
        return f"Error: old_text and new_text are identical. No changes made to {path}."
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        updated, found = _replace_nth(content, old_text, new_text, occurrence=occurrence)
        if not found:
            return f"Error: block not found in {path}"
        path.write_text(updated, encoding="utf-8")
        return f"Replaced block in {path}"
    except Exception as exc:
        return f"Error replacing block: {exc}"


def insert_after_in_file(path: Path, anchor_text: str, insert_text: str, occurrence: int = 1) -> str:
    if not path.exists():
        return f"Error: path not found: {path}"
    if not anchor_text:
        return "Error: anchor_text is required."
    if not insert_text:
        return f"Error: insert_text is empty. No changes made to {path}."
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        anchor_index = -1
        start = 0
        if occurrence < 1:
            occurrence = 1
        for _ in range(occurrence):
            anchor_index = content.find(anchor_text, start)
            if anchor_index < 0:
                break
            start = anchor_index + len(anchor_text)
        if anchor_index < 0:
            return f"Error: anchor not found in {path}"
        insert_at = anchor_index + len(anchor_text)
        updated = content[:insert_at] + insert_text + content[insert_at:]
        path.write_text(updated, encoding="utf-8")
        return f"Inserted text in {path}"
    except Exception as exc:
        return f"Error inserting text: {exc}"


def delete_block_in_file(path: Path, block_text: str, occurrence: int = 1) -> str:
    if not path.exists():
        return f"Error: path not found: {path}"
    if not block_text:
        return "Error: block_text is required."
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        updated, found = _replace_nth(content, block_text, "", occurrence=occurrence)
        if not found:
            return f"Error: block not found in {path}"
        path.write_text(updated, encoding="utf-8")
        return f"Deleted block in {path}"
    except Exception as exc:
        return f"Error deleting block: {exc}"


def _patch_path(raw: str, cwd: Path) -> Optional[Path]:
    raw = raw.strip()
    if raw == "/dev/null":
        return None
    if "\t" in raw:
        raw = raw.split("\t", 1)[0]
    if " " in raw:
        raw = raw.split(" ", 1)[0]
    if raw.startswith("a/") or raw.startswith("b/"):
        raw = raw[2:]
    return resolve_path(raw, cwd)


def _parse_hunk_header(line: str) -> Optional[tuple[int, int, int, int]]:
    match = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
    if not match:
        return None
    old_start = int(match.group(1))
    old_count = int(match.group(2) or "1")
    new_start = int(match.group(3))
    new_count = int(match.group(4) or "1")
    return old_start, old_count, new_start, new_count


def apply_unified_patch(patch_text: str, cwd: Path) -> str:
    if not patch_text.strip():
        return "Error: patch is required."

    lines = patch_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    file_patches: List[Dict[str, Any]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("diff --git "):
            index += 1
            continue
        if not line.startswith("--- "):
            index += 1
            continue

        old_path = _patch_path(line[4:].strip(), cwd)
        index += 1
        if index >= len(lines) or not lines[index].startswith("+++ "):
            return "Error: malformed patch; expected +++ after ---."
        new_path = _patch_path(lines[index][4:].strip(), cwd)
        index += 1

        hunks: List[List[str]] = []
        while index < len(lines):
            if lines[index].startswith("--- ") or lines[index].startswith("diff --git "):
                break
            if not lines[index].startswith("@@ "):
                index += 1
                continue
            hunk: List[str] = [lines[index]]
            index += 1
            while index < len(lines):
                current = lines[index]
                if current.startswith("@@ ") or current.startswith("--- ") or current.startswith("diff --git "):
                    break
                if current.startswith("\\ No newline at end of file"):
                    index += 1
                    continue
                if current and current[0] not in {" ", "+", "-"}:
                    return f"Error: malformed patch line: {current[:80]}"
                hunk.append(current)
                index += 1
            hunks.append(hunk)

        if not hunks:
            return "Error: patch contains a file header without hunks."
        file_patches.append({"old_path": old_path, "new_path": new_path, "hunks": hunks})

    if not file_patches:
        return "Error: no unified diff file patches found."

    updates: Dict[Path, Optional[str]] = {}
    touched: List[Path] = []
    for file_patch in file_patches:
        target_path = file_patch["new_path"] or file_patch["old_path"]
        if target_path is None:
            return "Error: patch cannot use /dev/null for both old and new paths."

        old_path = file_patch["old_path"]
        new_path = file_patch["new_path"]
        is_new_file = old_path is None
        is_delete = new_path is None

        if is_new_file:
            if target_path.exists():
                return f"Error: target file already exists: {target_path}"
            original_lines: List[str] = []
        else:
            if not target_path.exists():
                return f"Error: path not found: {target_path}"
            if target_path.is_dir():
                return f"Error: {target_path} is a directory."
            try:
                original_lines = target_path.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception as exc:
                return f"Error reading {target_path}: {exc}"

        result_lines = list(original_lines)
        offset = 0
        for hunk in file_patch["hunks"]:
            parsed = _parse_hunk_header(hunk[0])
            if parsed is None:
                return f"Error: malformed hunk header: {hunk[0]}"
            old_start, _old_count, _new_start, _new_count = parsed
            pos = max(old_start - 1 + offset, 0)

            old_segment: List[str] = []
            new_segment: List[str] = []
            for hunk_line in hunk[1:]:
                marker = hunk_line[:1]
                text = hunk_line[1:]
                if marker == " ":
                    old_segment.append(text)
                    new_segment.append(text)
                elif marker == "-":
                    old_segment.append(text)
                elif marker == "+":
                    new_segment.append(text)

            current_segment = result_lines[pos:pos + len(old_segment)]
            if current_segment != old_segment:
                return f"Error: patch context did not match {target_path} near line {old_start}."

            result_lines[pos:pos + len(old_segment)] = new_segment
            offset += len(new_segment) - len(old_segment)

        if is_delete:
            if result_lines:
                return f"Error: delete patch did not remove all content from {target_path}."
            updates[target_path] = None
        else:
            updates[target_path] = "\n".join(result_lines) + ("\n" if result_lines else "")
        touched.append(target_path)

    try:
        for path, content in updates.items():
            if content is None:
                path.unlink()
            else:
                if path.parent:
                    path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    except Exception as exc:
        return f"Error applying patch: {exc}"

    return "Applied patch:\n" + "\n".join(str(path) for path in touched)


def apply_fuzzy_unified_patch(patch_text: str, cwd: Path) -> str:
    if not patch_text.strip():
        return "Error: patch is required."

    lines = patch_text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    file_patches: List[Dict[str, Any]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("diff --git "):
            index += 1
            continue
        if not line.startswith("--- "):
            index += 1
            continue

        old_path = _patch_path(line[4:].strip(), cwd)
        index += 1
        if index >= len(lines) or not lines[index].startswith("+++ "):
            return "Error: malformed patch; expected +++ after ---."
        new_path = _patch_path(lines[index][4:].strip(), cwd)
        index += 1

        hunks: List[List[str]] = []
        while index < len(lines):
            if lines[index].startswith("--- ") or lines[index].startswith("diff --git "):
                break
            if not lines[index].startswith("@@ "):
                index += 1
                continue
            hunk: List[str] = [lines[index]]
            index += 1
            while index < len(lines):
                current = lines[index]
                if current.startswith("@@ ") or current.startswith("--- ") or current.startswith("diff --git "):
                    break
                if current.startswith("\\ No newline at end of file"):
                    index += 1
                    continue
                if current and current[0] not in {" ", "+", "-"}:
                    return f"Error: malformed patch line: {current[:80]}"
                hunk.append(current)
                index += 1
            hunks.append(hunk)

        if not hunks:
            return "Error: patch contains a file header without hunks."
        file_patches.append({"old_path": old_path, "new_path": new_path, "hunks": hunks})

    if not file_patches:
        return "Error: no unified diff file patches found."

    updates: Dict[Path, Optional[str]] = {}
    touched: List[Path] = []
    for file_patch in file_patches:
        target_path = file_patch["new_path"] or file_patch["old_path"]
        if target_path is None:
            return "Error: patch cannot use /dev/null for both old and new paths."

        old_path = file_patch["old_path"]
        new_path = file_patch["new_path"]
        is_new_file = old_path is None
        is_delete = new_path is None

        if is_new_file:
            if target_path.exists():
                return f"Error: target file already exists: {target_path}"
            original_lines: List[str] = []
        else:
            if not target_path.exists():
                return f"Error: path not found: {target_path}"
            if target_path.is_dir():
                return f"Error: {target_path} is a directory."
            try:
                original_lines = target_path.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception as exc:
                return f"Error reading {target_path}: {exc}"

        result_lines = list(original_lines)
        offset = 0
        for hunk in file_patch["hunks"]:
            parsed = _parse_hunk_header(hunk[0])
            if parsed is None:
                return f"Error: malformed hunk header: {hunk[0]}"
            old_start, _old_count, _new_start, _new_count = parsed
            pos = max(old_start - 1 + offset, 0)

            old_segment: List[str] = []
            new_segment: List[str] = []
            for hunk_line in hunk[1:]:
                marker = hunk_line[:1]
                text = hunk_line[1:]
                if marker == " ":
                    old_segment.append(text)
                    new_segment.append(text)
                elif marker == "-":
                    old_segment.append(text)
                elif marker == "+":
                    new_segment.append(text)

            current_segment = result_lines[pos:pos + len(old_segment)]
            if current_segment != old_segment:
                # Fuzzy window search (search +- 50 lines around pos)
                found_pos = -1
                search_radius = 50
                min_idx = max(0, pos - search_radius)
                max_idx = min(len(result_lines) - len(old_segment), pos + search_radius)
                
                # Check exact match within window
                for candidate in range(min_idx, max_idx + 1):
                    if result_lines[candidate:candidate + len(old_segment)] == old_segment:
                        found_pos = candidate
                        break
                
                # If exact match failed in window, check normalized line (ignore trailing space / CRLF)
                if found_pos == -1:
                    norm_old = [l.rstrip() for l in old_segment]
                    for candidate in range(min_idx, max_idx + 1):
                        cand_segment = [l.rstrip() for l in result_lines[candidate:candidate + len(old_segment)]]
                        if cand_segment == norm_old:
                            found_pos = candidate
                            break
                            
                if found_pos != -1:
                    pos = found_pos
                else:
                    return f"Error: patch context did not match {target_path} near line {old_start}."

            result_lines[pos:pos + len(old_segment)] = new_segment
            offset += len(new_segment) - len(old_segment)

        if is_delete:
            if result_lines:
                return f"Error: delete patch did not remove all content from {target_path}."
            updates[target_path] = None
        else:
            updates[target_path] = "\n".join(result_lines) + ("\n" if result_lines else "")
        touched.append(target_path)

    try:
        for path, content in updates.items():
            if content is None:
                path.unlink()
            else:
                if path.parent:
                    path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    except Exception as exc:
        return f"Error applying patch: {exc}"

    return "Applied patch:\n" + "\n".join(str(path) for path in touched)


def replace_lines_in_file(path: Path, start_line: int, end_line: int, new_text: str) -> str:
    if not path.exists():
        return f"Error: path not found: {path}"
    if start_line < 1:
        return "Error: start_line must be >= 1."
    if end_line < start_line:
        return "Error: end_line must be >= start_line."
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        if start_line > len(lines):
            return f"Error: start_line ({start_line}) exceeds file line count ({len(lines)})."
        
        # 1-indexed to 0-indexed bounds
        idx_start = start_line - 1
        idx_end = min(end_line, len(lines))
        
        new_lines = new_text.splitlines() if new_text else []
        if lines[idx_start:idx_end] == new_lines:
            return f"Error: lines {start_line}-{end_line} in {path} already match new_text. No changes made."
        lines[idx_start:idx_end] = new_lines
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return f"Replaced lines {start_line}-{end_line} in {path}"
    except Exception as exc:
        return f"Error replacing lines: {exc}"


def smart_replace_block_in_file(path: Path, old_text: str, new_text: str, occurrence: int = 1) -> str:
    if not path.exists():
        return f"Error: path not found: {path}"
    # Prevent infinite loop when AI attempts no-op replacement where old_text == new_text
    if old_text == new_text:
        return f"Error: old_text and new_text are identical. No changes made to {path}."
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        updated, found = _replace_nth(content, old_text, new_text, occurrence=occurrence)
        if found:
            path.write_text(updated, encoding="utf-8")
            return f"Replaced block in {path}"
            
        # Fallback 1: Normalized line endings (\r\n vs \n)
        norm_content = content.replace("\r\n", "\n")
        norm_old = old_text.replace("\r\n", "\n")
        norm_new = new_text.replace("\r\n", "\n")
        updated, found = _replace_nth(norm_content, norm_old, norm_new, occurrence=occurrence)
        if found:
            path.write_text(updated, encoding="utf-8")
            return f"Replaced block in {path} (matched normalized line endings)"
            
        # Fallback 2: Strip trailing whitespace on each line
        content_lines = norm_content.split("\n")
        old_lines = norm_old.split("\n")
        new_lines = norm_new.split("\n")
        
        target_norm_old = [l.rstrip() for l in old_lines]
        match_count = 0
        for i in range(len(content_lines) - len(old_lines) + 1):
            if [l.rstrip() for l in content_lines[i:i + len(old_lines)]] == target_norm_old:
                match_count += 1
                if match_count == occurrence:
                    content_lines[i:i + len(old_lines)] = new_lines
                    path.write_text("\n".join(content_lines) + "\n", encoding="utf-8")
                    return f"Replaced block in {path} (matched with trailing whitespace ignored)"
                    
        return f"Error: block not found in {path}"
    except Exception as exc:
        return f"Error replacing smart block: {exc}"


def verify_file_content(
    path: Path,
    expected_text: Optional[str] = None,
    unexpected_text: Optional[str] = None,
) -> str:
    if not path.exists():
        return f"Error: path not found: {path}"
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        failures = []
        if expected_text:
            norm_content = content.replace("\r\n", "\n")
            norm_exp = expected_text.replace("\r\n", "\n")
            if norm_exp not in norm_content:
                failures.append("expected_text was NOT found in file")
        if unexpected_text:
            norm_content = content.replace("\r\n", "\n")
            norm_unexp = unexpected_text.replace("\r\n", "\n")
            if norm_unexp in norm_content:
                failures.append("unexpected_text is STILL PRESENT in file")

        if failures:
            return f"VERIFICATION FAILED for {path}:\n" + "\n".join(f"- {f}" for f in failures)
        return f"VERIFICATION SUCCESSFUL: {path} matches expected state."
    except Exception as exc:
        return f"Error verifying file content: {exc}"



def list_directory(path: Path) -> str:
    try:
        if not path.exists():
            return f"Error: directory not found: {path}"
        if not path.is_dir():
            return f"Error: {path} is not a directory."
        entries = []
        for item in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            suffix = "/" if item.is_dir() else ""
            entries.append(f"{item.name}{suffix}")
        return "\n".join(entries) if entries else "Directory is empty."
    except Exception as exc:
        return f"Error listing directory: {exc}"


def get_system_info(cwd: Path) -> str:
    lines = [
        f"OS: {platform.system()} {platform.release()}",
        f"Python: {sys.version.split()[0]}",
        f"Time: {_now_stamp()}",
        f"CWD: {cwd}",
    ]
    return "\n".join(lines)


def run_shell_command(command: str, cwd: Path) -> str:
    if not command.strip():
        return "Error: no command provided."
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = (result.stdout or "") + (result.stderr or "")
        output = output.strip()
        return output if output else f"Done (exit code {result.returncode})"
    except subprocess.TimeoutExpired:
        return "Error: command timed out."
    except Exception as exc:
        return f"Error running shell command: {exc}"


def run_powershell_command(command: str, cwd: Path, timeout_seconds: int = 60) -> str:
    if not command.strip():
        return "Error: no command provided."
    timeout_seconds = max(1, min(int(timeout_seconds or 60), 300))
    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command,
            ],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        output = (result.stdout or "") + (result.stderr or "")
        output = output.strip()
        return output if output else f"Done (exit code {result.returncode})"
    except subprocess.TimeoutExpired:
        return "Error: PowerShell command timed out."
    except Exception as exc:
        return f"Error running PowerShell command: {exc}"


FUNCTIONS = {
    "read_file": {
        "name": "read_file",
        "description": "Read a local file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {"filepath": {"type": "STRING"}},
            "required": ["filepath"],
        },
    },
    "write_file": {
        "name": "write_file",
        "description": "Write content to a local file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING"},
                "content": {"type": "STRING"},
            },
            "required": ["filepath", "content"],
        },
    },
    "replace_file": {
        "name": "replace_file",
        "description": "Replace the full contents of a file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING"},
                "content": {"type": "STRING"},
            },
            "required": ["filepath", "content"],
        },
    },
    "delete_file": {
        "name": "delete_file",
        "description": "Delete a local file or directory.",
        "parameters": {
            "type": "OBJECT",
            "properties": {"filepath": {"type": "STRING"}},
            "required": ["filepath"],
        },
    },
    "list_directory": {
        "name": "list_directory",
        "description": "List directory contents.",
        "parameters": {
            "type": "OBJECT",
            "properties": {"path": {"type": "STRING"}},
            "required": ["path"],
        },
    },
    "get_system_info": {
        "name": "get_system_info",
        "description": "Get system information.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    "search_file": {
        "name": "search_file",
        "description": "Search text within a file or directory and return matching lines.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING"},
                "query": {"type": "STRING"},
                "recursive": {"type": "BOOLEAN"},
                "max_results": {"type": "INTEGER"},
            },
            "required": ["path", "query"],
        },
    },
    "search_web": {
        "name": "search_web",
        "description": "Search the web using the built-in no-key search provider.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING"},
                "max_results": {"type": "INTEGER"},
            },
            "required": ["query"],
        },
    },
    "search_tavily": {
        "name": "search_tavily",
        "description": "Search the web using saved Tavily API keys, trying the next key if one is limited.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING"},
                "max_results": {"type": "INTEGER"},
            },
            "required": ["query"],
        },
    },
    "inspect_image": {
        "name": "inspect_image",
        "description": "Inspect and load a local image file (PNG, JPG, WEBP, GIF, BMP) so Gemini can see and analyze its visual content in full resolution.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING", "description": "Local file path to the image file."}
            },
            "required": ["filepath"],
        },
    },
    "replace_block": {
        "name": "replace_block",
        "description": "Replace an exact block of text in a file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING"},
                "old_text": {"type": "STRING"},
                "new_text": {"type": "STRING"},
                "occurrence": {"type": "INTEGER"},
            },
            "required": ["filepath", "old_text", "new_text"],
        },
    },
    "insert_after": {
        "name": "insert_after",
        "description": "Insert text after an exact anchor in a file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING"},
                "anchor_text": {"type": "STRING"},
                "insert_text": {"type": "STRING"},
                "occurrence": {"type": "INTEGER"},
            },
            "required": ["filepath", "anchor_text", "insert_text"],
        },
    },
    "delete_block": {
        "name": "delete_block",
        "description": "Delete an exact block of text from a file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING"},
                "block_text": {"type": "STRING"},
                "occurrence": {"type": "INTEGER"},
            },
            "required": ["filepath", "block_text"],
        },
    },
    "apply_patch": {
        "name": "apply_patch",
        "description": "Apply a unified diff patch across one or more local files.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "patch": {
                    "type": "STRING",
                    "description": "A unified diff with ---/+++ file headers and @@ hunks.",
                },
            },
            "required": ["patch"],
        },
    },
    "fuzzy_apply_patch": {
        "name": "fuzzy_apply_patch",
        "description": "Apply a unified diff patch with +-50 line sliding window and line-ending/whitespace fallback.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "patch": {
                    "type": "STRING",
                    "description": "A unified diff with ---/+++ file headers and @@ hunks.",
                },
            },
            "required": ["patch"],
        },
    },
    "run_shell_command": {
        "name": "run_shell_command",
        "description": "Run a shell command.",
        "parameters": {
            "type": "OBJECT",
            "properties": {"command": {"type": "STRING"}},
            "required": ["command"],
        },
    },
    "run_powershell": {
        "name": "run_powershell",
        "description": "Run a PowerShell command for inspection, git checks, tests, or targeted local scripting. Use Select-String -SimpleMatch with single-quoted patterns for literal code searches.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "command": {"type": "STRING"},
                "timeout_seconds": {"type": "INTEGER"},
            },
            "required": ["command"],
        },
    },
    "request_follow_up": {
        "name": "request_follow_up",
        "description": "Request another turn for multi-step work.",
        "parameters": {
            "type": "OBJECT",
            "properties": {"reason": {"type": "STRING"}},
        },
    },
    "replace_lines": {
        "name": "replace_lines",
        "description": "Replace a specific range of 1-indexed line numbers in a file with new text.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING"},
                "start_line": {"type": "INTEGER"},
                "end_line": {"type": "INTEGER"},
                "new_text": {"type": "STRING"},
            },
            "required": ["filepath", "start_line", "end_line", "new_text"],
        },
    },
    "smart_replace_block": {
        "name": "smart_replace_block",
        "description": "Replace a block of text in a file with fuzzy fallback matching for line-endings and trailing whitespace.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING"},
                "old_text": {"type": "STRING"},
                "new_text": {"type": "STRING"},
                "occurrence": {"type": "INTEGER"},
            },
            "required": ["filepath", "old_text", "new_text"],
        },
    },
    "verify_file_content": {
        "name": "verify_file_content",
        "description": "Verify that a file contains expected_text and/or does not contain unexpected_text after making edits to confirm changes were successfully applied.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING"},
                "expected_text": {"type": "STRING", "description": "Snippet that must exist in the file."},
                "unexpected_text": {"type": "STRING", "description": "Snippet that must NOT exist in the file (e.g. old code removed)."},
            },
            "required": ["filepath"],
        },
    },
    "save_memory": {
        "name": "save_memory",
        "description": f"Save important notes, user profile details (e.g. name, preferences), or project facts into memory. You MUST call this immediately when the user shares personal details (like name) or preferences. Default path='main'. DO NOT use save_memory for creating/saving skills; skills MUST be saved using write_file into '{SKILLS_DIR.as_posix()}/<skill_name>.md'.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "key": {"type": "STRING", "description": "Unique key/label for the memory item (e.g., 'user_name', 'preferred_language', 'coding_style')."},
                "content": {"type": "STRING", "description": "The memory content or fact text to save."},
                "path": {"type": "STRING", "description": "Memory path inside 'memory/' (default: 'main'). E.g., 'main', 'user/profile.md', 'database/schema.json'."},
                "description": {"type": "STRING", "description": "Short summary of what this sub-memory file/folder contains."},
            },
            "required": ["key", "content"],
        },
    },
    "read_memory": {
        "name": "read_memory",
        "description": "Retrieve saved memories. Specify path='main' (or omit) to read main memory & sub-memory index, or specify a sub-memory path like 'database/schema' to read deep topic memory.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "Memory path inside 'memory/' (e.g., 'main', 'database/schema'). Defaults to 'main'."},
                "key": {"type": "STRING", "description": "Optional specific key to query within that memory file."},
            },
        },
    },
    "list_memories": {
        "name": "list_memories",
        "description": "List all memory files, subfolders, and items in the memory directory structure.",
        "parameters": {"type": "OBJECT", "properties": {}},
    },
    "delete_memory": {
        "name": "delete_memory",
        "description": "Delete a specific memory key or an entire sub-memory file/folder.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "Memory path inside 'memory/' (e.g., 'main', 'database/schema'). Defaults to 'main'."},
                "key": {"type": "STRING", "description": "Key to delete. If omitted for a sub-memory path, deletes the entire sub-memory file."},
            },
        },
    },

}


def execute_tool(name: str, args: Dict[str, Any], cwd: Path, tavily_accounts: Optional[Dict[str, str]] = None) -> str:
    if name == "read_file":
        filepath = args.get("filepath", "")
        return read_file(resolve_path(filepath, cwd))
    if name == "write_file":
        filepath = args.get("filepath", "")
        content = args.get("content", "")
        return write_file(resolve_path(filepath, cwd), content)
    if name == "replace_file":
        filepath = args.get("filepath", "")
        content = args.get("content", "")
        return replace_file(resolve_path(filepath, cwd), content)
    if name == "delete_file":
        filepath = args.get("filepath", "")
        return delete_path(resolve_path(filepath, cwd))
    if name == "list_directory":
        path = args.get("path", ".")
        return list_directory(resolve_path(path, cwd))
    if name == "get_system_info":
        return get_system_info(cwd)
    if name == "search_file":
        path = resolve_path(args.get("path", "."), cwd)
        query = str(args.get("query", ""))
        recursive = bool(args.get("recursive", False))
        max_results = int(args.get("max_results", 20) or 20)
        return search_file(path, query, recursive=recursive, max_results=max_results)
    if name == "search_web":
        return search_web(str(args.get("query", "")), max_results=int(args.get("max_results", 5) or 5))
    if name == "search_tavily":
        return search_tavily(
            str(args.get("query", "")),
            tavily_accounts or {},
            max_results=int(args.get("max_results", 5) or 5),
        )
    if name == "inspect_image":
        filepath = resolve_path(args.get("filepath", ""), cwd)
        info_str, _ = inspect_image_file(filepath)
        return info_str
    if name == "replace_block":
        filepath = resolve_path(args.get("filepath", ""), cwd)
        old_text = str(args.get("old_text", ""))
        new_text = str(args.get("new_text", ""))
        occurrence = int(args.get("occurrence", 1) or 1)
        return replace_block_in_file(filepath, old_text, new_text, occurrence=occurrence)
    if name == "smart_replace_block":
        filepath = resolve_path(args.get("filepath", ""), cwd)
        old_text = str(args.get("old_text", ""))
        new_text = str(args.get("new_text", ""))
        occurrence = int(args.get("occurrence", 1) or 1)
        return smart_replace_block_in_file(filepath, old_text, new_text, occurrence=occurrence)
    if name == "verify_file_content":
        filepath = resolve_path(args.get("filepath", ""), cwd)
        expected_text = args.get("expected_text")
        unexpected_text = args.get("unexpected_text")
        return verify_file_content(filepath, expected_text, unexpected_text)
    if name == "save_memory":
        key = str(args.get("key", ""))
        content = str(args.get("content", ""))
        path = str(args.get("path", "main"))
        description = str(args.get("description", ""))
        return save_memory(key, content, path=path, description=description)
    if name == "read_memory":
        path = str(args.get("path", "main"))
        key = args.get("key")
        return read_memory(path=path, key=str(key) if key is not None else None)
    if name == "list_memories":
        return list_memories()
    if name == "delete_memory":
        path = str(args.get("path", "main"))
        key = args.get("key")
        return delete_memory_item(path=path, key=str(key) if key is not None else None)


    if name == "replace_lines":
        filepath = resolve_path(args.get("filepath", ""), cwd)
        start_line = int(args.get("start_line", 1) or 1)
        end_line = int(args.get("end_line", 1) or 1)
        new_text = str(args.get("new_text", ""))
        return replace_lines_in_file(filepath, start_line, end_line, new_text)
    if name == "insert_after":
        filepath = resolve_path(args.get("filepath", ""), cwd)
        anchor_text = str(args.get("anchor_text", ""))
        insert_text = str(args.get("insert_text", ""))
        occurrence = int(args.get("occurrence", 1) or 1)
        return insert_after_in_file(filepath, anchor_text, insert_text, occurrence=occurrence)
    if name == "delete_block":
        filepath = resolve_path(args.get("filepath", ""), cwd)
        block_text = str(args.get("block_text", ""))
        occurrence = int(args.get("occurrence", 1) or 1)
        return delete_block_in_file(filepath, block_text, occurrence=occurrence)
    if name == "apply_patch":
        return apply_unified_patch(str(args.get("patch", "")), cwd)
    if name == "fuzzy_apply_patch":
        return apply_fuzzy_unified_patch(str(args.get("patch", "")), cwd)
    if name == "run_shell_command":
        return run_shell_command(str(args.get("command", "")), cwd)
    if name == "run_powershell":
        return run_powershell_command(
            str(args.get("command", "")),
            cwd,
            timeout_seconds=int(args.get("timeout_seconds", 60) or 60),
        )
    if name == "request_follow_up":
        reason = args.get("reason") or "Continuing..."
        return f"Follow-up turn granted: {reason}"
    return f"Unknown tool: {name}"


_TOOLS_CACHE: Optional[List[Dict[str, str]]] = None


def list_tool_catalog() -> List[Dict[str, str]]:
    """Load tool catalog from tools.json. Falls back to hardcoded defaults if missing."""
    global _TOOLS_CACHE
    if _TOOLS_CACHE is not None:
        return _TOOLS_CACHE
    try:
        if TOOLS_FILE.exists():
            data = json.loads(TOOLS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list) and len(data) > 0:
                _TOOLS_CACHE = data
                return _TOOLS_CACHE
    except Exception:
        pass
    # Hardcoded fallback (should not be reached if tools.json exists)
    _TOOLS_CACHE = [
        {"name": "read_file", "category": "Inspection & File System", "rating": "Best (Essential)", "description": "Read a local file."},
        {"name": "write_file", "category": "Code Modifications", "rating": "Use with caution (Overwrites)", "description": "Write content to a local file."},
        {"name": "replace_file", "category": "Code Modifications", "rating": "Use with caution (Overwrites full file)", "description": "[Code-Merge] Replace full contents of a file."},
        {"name": "delete_file", "category": "Inspection & File System", "rating": "Destructive", "description": "Delete a local file or directory."},
        {"name": "list_directory", "category": "Inspection & File System", "rating": "Best (Safe)", "description": "List directory contents."},
        {"name": "get_system_info", "category": "Inspection & File System", "rating": "Best (Safe)", "description": "Get system information."},
        {"name": "search_file", "category": "Inspection & File System", "rating": "Best (Safe)", "description": "Search text within a file or directory."},
        {"name": "search_web", "category": "Inspection & File System", "rating": "Safe", "description": "Search the web without a saved API key."},
        {"name": "search_tavily", "category": "Inspection & File System", "rating": "Safe", "description": "Search the web with saved Tavily API keys."},
        {"name": "fuzzy_apply_patch", "category": "Code Modifications", "rating": "Best for multi-file changes (Resilient)", "description": "[Code-Merge] Unified diff with fuzzy window fallback."},
        {"name": "smart_replace_block", "category": "Code Modifications", "rating": "Best for targeted edits (High accuracy)", "description": "[Code-Merge] Replace block with fuzzy fallback."},
        {"name": "verify_file_content", "category": "Code Modifications", "rating": "Best for post-edit verification", "description": "Verify that expected_text exists and/or unexpected_text is absent after modifications."},

        {"name": "replace_lines", "category": "Code Modifications", "rating": "Best for exact line ranges (Low token)", "description": "[Code-Merge] Replace 1-indexed line range."},
        {"name": "replace_block", "category": "Code Modifications", "rating": "Good (Requires exact text match)", "description": "[Code-Merge] Replace an exact block of text in a file."},
        {"name": "apply_patch", "category": "Code Modifications", "rating": "Strict (Fails on small line drifts)", "description": "[Code-Merge] Apply a strict unified diff across files."},
        {"name": "insert_after", "category": "Code Modifications", "rating": "Good (Targeted insertion)", "description": "[Code-Merge] Insert text after an exact anchor."},
        {"name": "delete_block", "category": "Code Modifications", "rating": "Good (Targeted removal)", "description": "[Code-Merge] Delete an exact block of text from a file."},
        {"name": "run_shell_command", "category": "Execution & Shell", "rating": "Powerful (Command execution)", "description": "Run a shell command."},
        {"name": "run_powershell", "category": "Execution & Shell", "rating": "Best for Windows inspection & tests", "description": "Run a PowerShell command."},
        {"name": "request_follow_up", "category": "Control Flow", "rating": "Safe", "description": "Request another turn for multi-step work."},
    ]
    return _TOOLS_CACHE


def tool_name_set() -> Set[str]:
    return {tool["name"] for tool in list_tool_catalog()}


def enabled_tool_names(disabled_tools: Set[str]) -> List[str]:
    disabled = set(disabled_tools)
    return [tool["name"] for tool in list_tool_catalog() if tool["name"] not in disabled]


def format_cooldown_until(until: Optional[dt.datetime]) -> str:
    if until is None:
        return ""
    remaining = int((until - _now()).total_seconds() + 0.999)
    if remaining <= 0:
        return ""
    return _format_seconds(remaining)


class GeminiClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def count_tokens(
        self,
        contents: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
    ) -> int:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{urllib.parse.quote(self.model, safe='')}:countTokens?key={urllib.parse.quote(self.api_key)}"
        )
        payload: Dict[str, Any] = {"contents": contents}
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read().decode("utf-8", errors="replace")
                body = json.loads(raw)
                return int(body.get("totalTokens", 0))
        except Exception:
            return 0

    def generate(
        self,
        contents: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        tool_names: Optional[List[str]] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 2048,
    ) -> Dict[str, Any]:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{urllib.parse.quote(self.model, safe='')}:generateContent?key={urllib.parse.quote(self.api_key)}"
        )
        payload: Dict[str, Any] = {"contents": contents}
        if tool_names is None:
            payload["tools"] = [{"functionDeclarations": list(FUNCTIONS.values())}]
        else:
            declarations = [FUNCTIONS[name] for name in tool_names if name in FUNCTIONS]
            if declarations:
                payload["tools"] = [{"functionDeclarations": declarations}]
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        payload["generationConfig"] = {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        }

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                raw = response.read().decode("utf-8", errors="replace")
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except Exception:
                body = {"error": {"message": raw or str(exc)}}
            raise RuntimeError(body.get("error", {}).get("message", str(exc))) from exc
        except Exception as exc:
            raise RuntimeError(str(exc)) from exc

    def list_models(self) -> List[Dict[str, Any]]:
        models: List[Dict[str, Any]] = []
        page_token: Optional[str] = None

        while True:
            query = {"pageSize": str(MODELS_PAGE_SIZE)}
            if page_token:
                query["pageToken"] = page_token

            url = (
                "https://generativelanguage.googleapis.com/v1beta/models"
                f"?{urllib.parse.urlencode(query)}&key={urllib.parse.quote(self.api_key)}"
            )
            request = urllib.request.Request(url, method="GET")
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    raw = response.read().decode("utf-8", errors="replace")
                    body = json.loads(raw)
            except urllib.error.HTTPError as exc:
                raw = exc.read().decode("utf-8", errors="replace")
                try:
                    body = json.loads(raw)
                except Exception:
                    body = {"error": {"message": raw or str(exc)}}
                raise RuntimeError(body.get("error", {}).get("message", str(exc))) from exc
            except Exception as exc:
                raise RuntimeError(str(exc)) from exc

            models.extend(body.get("models", []))
            page_token = body.get("nextPageToken")
            if not page_token:
                break

        return models


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").strip()
    return text


def _style_text(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def _render_inline_markdown(text: str) -> str:
    if not text:
        return text

    def replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        url = match.group(2)
        if sys.stdout.isatty():
            return f"{_style_text(label, '4;36')} ({url})"
        return f"{label} ({url})"

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, text)
    # Handle bold tags robustly, stripping leftover dangling asterisks if markdown is malformed
    # Match bold and italic cleanly, handling single or double asterisks robustly
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: _style_text(m.group(1), "1"), text)
    text = re.sub(r"__(.+?)__", lambda m: _style_text(m.group(1), "1"), text)
    text = re.sub(r"\*(?!\s)(.+?)(?<!\s)\*", lambda m: _style_text(m.group(1), "3"), text)
    text = re.sub(r"_(?!\s)(.+?)(?<!\s)_", lambda m: _style_text(m.group(1), "3"), text)
    text = re.sub(r"`([^`]+)`", lambda m: _style_text(m.group(1), "38;5;214"), text)
    # Remove any remaining stray single or double asterisks that didn't form a closed pair
    text = re.sub(r"(?<!\w)\*{1,2}|\*{1,2}(?!\w)", "", text)
    return text


def _wrap_visible(text: str, max_width: int) -> List[str]:
    """Wraps text containing ANSI codes into multiple lines based on visible width."""
    max_width = max(1, max_width)
    if _visible_len(text) <= max_width:
        return [text]

    ansi_pattern = re.compile(r'(\x1b\[[0-9;?]*[a-zA-Z])')
    parts = ansi_pattern.split(text)

    items = []
    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2 == 1:
            items.append((part, True))
        else:
            for char in part:
                if char in ('\ufe0f', '\ufe0e'):
                    continue
                items.append((char, False))

    words = []
    current_word = []

    for item in items:
        content, is_ansi = item
        if not is_ansi and content == ' ':
            if current_word:
                words.append(current_word)
                current_word = []
            words.append([(content, False)])
        else:
            current_word.append(item)
    if current_word:
        words.append(current_word)

    def word_vis_len(w):
        return sum(_char_width(c) for c, is_ansi in w if not is_ansi)

    split_words = []
    for w in words:
        v_len = word_vis_len(w)
        if v_len <= max_width or (len(w) == 1 and not w[0][1] and w[0][0] == ' '):
            split_words.append(w)
        else:
            chunk = []
            chunk_vis = 0
            for item in w:
                c, is_ansi = item
                if is_ansi:
                    chunk.append(item)
                else:
                    cw = _char_width(c)
                    if chunk_vis + cw > max_width and chunk:
                        split_words.append(chunk)
                        chunk = []
                        chunk_vis = 0
                    chunk.append(item)
                    chunk_vis += cw
            if chunk:
                split_words.append(chunk)

    lines = []
    cur_line_items = []
    cur_line_vis = 0
    active_ansi = []

    for w in split_words:
        w_vis = word_vis_len(w)
        is_space = (len(w) == 1 and not w[0][1] and w[0][0] == ' ')

        if is_space:
            if cur_line_vis > 0 and cur_line_vis + 1 <= max_width:
                cur_line_items.extend(w)
                cur_line_vis += 1
            continue

        if cur_line_vis > 0 and cur_line_vis + w_vis > max_width:
            line_str = "".join(c for c, _ in cur_line_items)
            if active_ansi:
                line_str += "\033[0m"
            lines.append(line_str)

            cur_line_items = []
            if active_ansi:
                for code in active_ansi:
                    cur_line_items.append((code, True))
            cur_line_vis = 0

        for c, is_ansi in w:
            cur_line_items.append((c, is_ansi))
            if is_ansi:
                if c in ("\033[0m", "\x1b[0m", "\x1b[m"):
                    active_ansi.clear()
                else:
                    active_ansi.append(c)
            else:
                cur_line_vis += _char_width(c)

    if cur_line_items:
        line_str = "".join(c for c, _ in cur_line_items)
        if active_ansi:
            line_str += "\033[0m"
        lines.append(line_str)

    return lines if lines else [text]

def render_markdown_text(text: str) -> str:
    lines: List[str] = []
    in_code_block = False
    raw_lines = text.splitlines()
    idx = 0
    
    # Get terminal width for intelligent table wrapping
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
            lines.append(_style_text(line, "90"))
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
                # Parse
                grid = []
                for row in table_rows:
                    row_content = row.strip()
                    if row_content.startswith("|"): row_content = row_content[1:]
                    if row_content.endswith("|"): row_content = row_content[:-1]
                    row_content = row_content.replace(r"\|", "\x00PIPE\x00")
                    cells = [c.strip().replace("\x00PIPE\x00", "|") for c in row_content.split("|")]
                    is_sep = all(set(c.replace(" ", "")) <= {"-", ":"} and "-" in c for c in cells) if cells else False
                    rendered = [_render_inline_markdown(c) for c in cells] if not is_sep else []
                    grid.append({"rendered": rendered, "is_sep": is_sep})
                
                non_sep_rows = [r for r in grid if not r["is_sep"]]
                col_count = max((len(r["rendered"]) for r in non_sep_rows), default=0)

                if col_count > 0:
                    # Calculate basic widths
                    col_widths = [0] * col_count
                    for row in grid:
                        if row["is_sep"]: continue
                        for c_idx, cell in enumerate(row["rendered"]):
                            if c_idx < col_count:
                                col_widths[c_idx] = max(col_widths[c_idx], _visible_len(cell))
                    
                    col_widths = [max(1, w) for w in col_widths]

                    # Constrain width if table exceeds terminal
                    total_w = sum(col_widths) + (col_count * 3) + 1
                    if total_w > term_width:
                        avail_w = max(col_count * 4, term_width - (col_count * 3 + 1))
                        min_w = max(4, avail_w // (col_count * 2))
                        curr_sum = sum(col_widths)
                        if curr_sum > 0:
                            col_widths = [
                                max(min_w, int(w * avail_w / curr_sum))
                                for w in col_widths
                            ]
                        while sum(col_widths) > avail_w:
                            max_idx = max(range(col_count), key=lambda i: col_widths[i])
                            if col_widths[max_idx] <= min_w:
                                break
                            col_widths[max_idx] -= 1

                    border_color = "36"
                    def get_sep_line(left, mid, right):
                        return _style_text(left + mid.join("─" * (w + 2) for w in col_widths) + right, border_color)

                    lines.append(get_sep_line("┌", "┬", "┐"))
                    v_bar = _style_text("│", border_color)

                    for r_idx, row in enumerate(grid):
                        if row["is_sep"]:
                            lines.append(get_sep_line("├", "┼", "┤"))
                            continue
                        
                        # Multi-line cell wrapping (handles <br> and \n)
                        wrapped_cells = []
                        for c_idx in range(col_count):
                            content = row["rendered"][c_idx] if c_idx < len(row["rendered"]) else ""
                            content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
                            cell_lines = []
                            for paragraph in content.split('\n'):
                                cell_lines.extend(_wrap_visible(paragraph, col_widths[c_idx]))
                            wrapped_cells.append(cell_lines if cell_lines else [""])
                        
                        row_height = max((len(c) for c in wrapped_cells), default=1)
                        
                        # Render all lines of this row
                        for sub_idx in range(row_height):
                            line_parts = []
                            for c_idx in range(col_count):
                                cell_lines = wrapped_cells[c_idx]
                                cell_line = cell_lines[sub_idx] if sub_idx < len(cell_lines) else ""
                                pad_len = max(0, col_widths[c_idx] - _visible_len(cell_line))
                                pad = " " * pad_len
                                line_parts.append(f" {cell_line}{pad} ")
                            lines.append(f"{v_bar}{v_bar.join(line_parts)}{v_bar}")

                        # Separator between content rows
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
                lines.append(_style_text(content, color))
            else:
                lines.append(_render_inline_markdown(line))
        elif re.match(r"^\s*[-*+]\s+", line):
            lines.append(f"• {_render_inline_markdown(stripped_line.lstrip('-*+ '))}")
        elif re.match(r"^\s*\d+\.\s+", line):
            lines.append(_render_inline_markdown(line))
        elif stripped_line.startswith(">"):
            lines.append(f"{_style_text('> ', '90')}{_render_inline_markdown(stripped_line[1:].strip())}")
        elif re.match(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", stripped_line):
            lines.append(_style_text("─" * 32, "90"))
        else:
            lines.append(_render_inline_markdown(line))
        
        idx += 1

    return "\n".join(lines).strip()


def _format_tool_value(value: Any) -> str:
    if isinstance(value, str):
        text = value.rstrip()
        if "\n" in text or len(text) > 120:
            return "\n".join(f"    {line}" for line in text.splitlines())
        return text
    if isinstance(value, (dict, list)):
        return textwrap.indent(json.dumps(value, indent=2, ensure_ascii=False), "    ")
    return str(value)


def _format_patch_preview(patch_text: str) -> List[str]:
    lines: List[str] = []
    for raw_line in patch_text.rstrip().splitlines():
        if raw_line.startswith(("--- ", "+++ ")):
            styled = _ansi_wrap(raw_line, "1")
        elif raw_line.startswith("@@ "):
            styled = _ansi_wrap(raw_line, "36")
        elif raw_line.startswith("+"):
            styled = _ansi_wrap(raw_line, "32")
        elif raw_line.startswith("-"):
            styled = _ansi_wrap(raw_line, "31")
        else:
            styled = raw_line
        lines.append(f"    {styled}")
    return lines


def format_tool_call(name: str, args: Dict[str, Any]) -> str:
    if name in {"run_shell_command", "run_powershell"}:
        command = str(args.get("command", "")).rstrip()
        label = "PowerShell" if name == "run_powershell" else "shell"
        if "\n" in command:
            return "Ran " + label + " script:\n" + "\n".join(f"  {line}" for line in command.splitlines())
        if command:
            return f"Ran {command}"

    if name in {"apply_patch", "fuzzy_apply_patch"} and isinstance(args.get("patch"), str):
        lines = [f"[tool] {name}", "  patch:"]
        lines.extend(_format_patch_preview(str(args.get("patch", ""))))
        return "\n".join(lines)

    if name in {"smart_replace_block", "replace_block"}:
        filepath = args.get("filepath", "")
        old_text = str(args.get("old_text", ""))
        new_text = str(args.get("new_text", ""))
        occ = args.get("occurrence")
        lines = [f"[tool] {name}", f"  filepath: {filepath}"]
        if occ and int(occ) > 1:
            lines.append(f"  occurrence: {occ}")
        lines.append("  old_text (removed):")
        for l in old_text.rstrip().splitlines():
            lines.append(f"    {_ansi_wrap('- ' + l, '31')}")
        lines.append("  new_text (added):")
        for l in new_text.rstrip().splitlines():
            lines.append(f"    {_ansi_wrap('+ ' + l, '32')}")
        return "\n".join(lines)

    if name == "replace_lines":
        filepath = args.get("filepath", "")
        start_line = args.get("start_line", "")
        end_line = args.get("end_line", "")
        new_text = str(args.get("new_text", ""))
        lines = [f"[tool] {name}", f"  filepath: {filepath}", f"  lines: {start_line}-{end_line}", "  new_text (added):"]
        for l in new_text.rstrip().splitlines():
            lines.append(f"    {_ansi_wrap('+ ' + l, '32')}")
        return "\n".join(lines)

    if name == "insert_after":
        filepath = args.get("filepath", "")
        anchor_text = str(args.get("anchor_text", ""))
        insert_text = str(args.get("insert_text", ""))
        lines = [f"[tool] {name}", f"  filepath: {filepath}", f"  after anchor: {anchor_text}", "  insert_text (added):"]
        for l in insert_text.rstrip().splitlines():
            lines.append(f"    {_ansi_wrap('+ ' + l, '32')}")
        return "\n".join(lines)

    if name == "delete_block":
        filepath = args.get("filepath", "")
        block_text = str(args.get("block_text", ""))
        lines = [f"[tool] {name}", f"  filepath: {filepath}", "  block_text (removed):"]
        for l in block_text.rstrip().splitlines():
            lines.append(f"    {_ansi_wrap('- ' + l, '31')}")
        return "\n".join(lines)

    lines = [f"[tool] {name}"]
    if not args:
        return "\n".join(lines)
    for key in sorted(args):
        value = args[key]
        if isinstance(value, str) and ("\n" in value.rstrip() or len(value) > 120):
            lines.append(f"  {key}:")
            lines.extend(_format_tool_value(value).splitlines())
        else:
            lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value}")
    return "\n".join(lines)


def format_tool_result(result: str) -> str:
    text = result[:4000].rstrip()
    is_err = text.lower().startswith("error") or "error:" in text.lower()
    header = _ansi_wrap("[tool-result: ERROR]", "31") if is_err else "[tool-result]"
    lines = [header]
    if text:
        for line in text.splitlines():
            lines.append(f"  {_ansi_wrap(line, '31')}" if is_err else f"  {line}")
    else:
        lines.append("  <empty>")
    if len(result) > 4000:
        lines.append("  ... (truncated)")
    return "\n".join(lines)


def render_model_parts(parts: List[Dict[str, Any]]) -> str:
    chunks: List[str] = []
    for part in parts:
        if "text" in part:
            chunk = normalize_text(str(part["text"]))
            if chunk:
                chunks.append(chunk)
    return render_markdown_text("\n\n".join(chunks).strip())


def extract_function_calls(parts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    calls: List[Dict[str, Any]] = []
    for part in parts:
        if "functionCall" in part:
            calls.append(part["functionCall"])
    return calls


def load_transcript(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Transcript must be a JSON object.")
    return data


def save_transcript(path: Path, state: Dict[str, Any]) -> str:
    if path.parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"Transcript saved to {path}"


def _require_api_crypto() -> None:
    if AES is None or PBKDF2 is None or get_random_bytes is None:
        raise RuntimeError("Encrypted API account storage requires pycryptodome.")


def _prompt_password(action: str) -> str:
    prompt = f"{action} password: "
    try:
        return getpass.getpass(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""
    except Exception:
        return input(prompt).strip()


def _pack_locked_part(part: bytes) -> bytes:
    return len(part).to_bytes(4, "big") + part


def _unpack_locked_part(data: bytes, offset: int) -> tuple[bytes, int]:
    if offset + 4 > len(data):
        raise ValueError("Locked API account file is truncated.")
    size = int.from_bytes(data[offset:offset + 4], "big")
    offset += 4
    if offset + size > len(data):
        raise ValueError("Locked API account file is truncated.")
    return data[offset:offset + size], offset + size


def normalize_api_account_payload(data: Any) -> Dict[str, Dict[str, str]]:
    if not isinstance(data, dict):
        return {"accounts": {}, "tavily_accounts": {}}
    accounts = data.get("accounts", {})
    tavily_accounts = data.get("tavily_accounts", {})
    if not isinstance(accounts, dict):
        accounts = {}
    if not isinstance(tavily_accounts, dict):
        tavily_accounts = {}
    return {
        "accounts": {str(name): str(key) for name, key in accounts.items()},
        "tavily_accounts": {str(name): str(key) for name, key in tavily_accounts.items()},
    }


def _encrypt_api_accounts(
    accounts: Dict[str, str],
    password: str,
    tavily_accounts: Optional[Dict[str, str]] = None,
) -> bytes:
    _require_api_crypto()
    payload = json.dumps(
        {
            "accounts": dict(sorted(accounts.items())),
            "tavily_accounts": dict(sorted((tavily_accounts or {}).items())),
        },
        indent=2,
        ensure_ascii=False,
    ).encode("utf-8")
    salt = get_random_bytes(16)
    key = PBKDF2(password.encode("utf-8"), salt, dkLen=32, count=200_000)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(payload)
    parts = [
        API_ACCOUNTS_MAGIC,
        _pack_locked_part(salt),
        _pack_locked_part(cipher.nonce),
        _pack_locked_part(tag),
        _pack_locked_part(ciphertext),
    ]
    return b"".join(parts)


def _decrypt_api_accounts(blob: bytes, password: str) -> Dict[str, Any]:
    _require_api_crypto()
    if not blob.startswith(API_ACCOUNTS_MAGIC):
        raise ValueError("Invalid locked API account file.")
    offset = len(API_ACCOUNTS_MAGIC)
    salt, offset = _unpack_locked_part(blob, offset)
    nonce, offset = _unpack_locked_part(blob, offset)
    tag, offset = _unpack_locked_part(blob, offset)
    ciphertext, offset = _unpack_locked_part(blob, offset)
    if offset != len(blob):
        raise ValueError("Invalid locked API account file.")
    key = PBKDF2(password.encode("utf-8"), salt, dkLen=32, count=200_000)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    data = json.loads(plaintext.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Locked API account file is invalid.")
    return normalize_api_account_payload(data)


def empty_account_model_prefs() -> Dict[str, Any]:
    return {
        "hidden_models": [],
        "speed_tags": {},
        "model_usage_counts": {},
        "failover_uses": 0,
    }


def normalize_account_model_prefs(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        return empty_account_model_prefs()
    hidden = data.get("hidden_models", [])
    if not isinstance(hidden, list):
        hidden = []
    speed_tags = data.get("speed_tags", {})
    if not isinstance(speed_tags, dict):
        speed_tags = {}
    usage_counts = data.get("model_usage_counts", {})
    if not isinstance(usage_counts, dict):
        usage_counts = {}
    failover_uses = data.get("failover_uses", 0)
    try:
        failover_uses = int(failover_uses)
    except Exception:
        failover_uses = 0
    return {
        "hidden_models": [str(item) for item in hidden],
        "speed_tags": {str(k): str(v) for k, v in speed_tags.items()},
        "model_usage_counts": {str(k): int(v) for k, v in usage_counts.items()},
        "failover_uses": max(0, int(failover_uses)),
    }


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "enabled"}
    return bool(value)


def default_model_prefs() -> Dict[str, Any]:
    return {
        **empty_account_model_prefs(),
        "api_accounts": {},
        "disabled_tools": [],
        "aliases": {},
        "last_model": DEFAULT_MODEL,
        "last_api_account": "",
        "system_instruction": DEFAULT_SYSTEM,
        "tool_loop_limit": DEFAULT_TOOL_LOOPS,
        "auto_failover_default": False,
        "auto_failover_projects": {},
        "prompt_fg": "ansired",
        "prompt_bg": "",
        "prompt_prefix_color": "1;32",
    }


def load_model_prefs() -> Dict[str, Any]:
    if not MODEL_PREFS_FILE.exists():
        return default_model_prefs()
    try:
        data = json.loads(MODEL_PREFS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return default_model_prefs()
        account_model_prefs = normalize_account_model_prefs(data)
        api_accounts = data.get("api_accounts", {})
        if not isinstance(api_accounts, dict):
            api_accounts = {}
        normalized_api_accounts = {
            str(account_name): normalize_account_model_prefs(account_prefs)
            for account_name, account_prefs in api_accounts.items()
        }
        last_api_account = str(data.get("last_api_account") or "")
        if last_api_account and last_api_account not in normalized_api_accounts:
            normalized_api_accounts[last_api_account] = account_model_prefs
        account_usage_sources = list(normalized_api_accounts.values())
        if account_usage_sources:
            merged_hidden = set(account_model_prefs.get("hidden_models", []))
            merged_speed_tags = dict(account_model_prefs.get("speed_tags", {}))
            merged_usage_counts: Dict[str, int] = {
                str(model): int(count)
                for model, count in dict(account_model_prefs.get("model_usage_counts", {})).items()
            }
            for account_prefs in account_usage_sources:
                merged_hidden.update(str(item) for item in account_prefs.get("hidden_models", []))
                merged_speed_tags.update({str(k): str(v) for k, v in dict(account_prefs.get("speed_tags", {})).items()})
                for model, count in dict(account_prefs.get("model_usage_counts", {})).items():
                    model_key = str(model)
                    merged_usage_counts[model_key] = int(merged_usage_counts.get(model_key, 0) or 0) + int(count)
            account_model_prefs["hidden_models"] = sorted(merged_hidden)
            account_model_prefs["speed_tags"] = merged_speed_tags
            account_model_prefs["model_usage_counts"] = merged_usage_counts
        disabled_tools = data.get("disabled_tools", [])
        if not isinstance(disabled_tools, list):
            disabled_tools = []
        aliases = data.get("aliases", {})
        if not isinstance(aliases, dict):
            aliases = {}
        auto_failover_projects = data.get("auto_failover_projects", {})
        if not isinstance(auto_failover_projects, dict):
            auto_failover_projects = {}
        prefs = dict(account_model_prefs)
        prefs.update({
            "api_accounts": normalized_api_accounts,
            "disabled_tools": [str(item) for item in disabled_tools],
            "aliases": {str(k): str(v) for k, v in aliases.items()},
            "last_model": str(data.get("last_model") or DEFAULT_MODEL),
            "last_api_account": last_api_account,
            "system_instruction": str(data.get("system_instruction") or DEFAULT_SYSTEM),
            "tool_loop_limit": int(data.get("tool_loop_limit") or DEFAULT_TOOL_LOOPS),
            "auto_failover_default": normalize_bool(data.get("auto_failover_default", False)),
            "auto_failover_projects": {
                str(project_root): normalize_bool(enabled)
                for project_root, enabled in auto_failover_projects.items()
            },
            "prompt_fg": str(data.get("prompt_fg") or "ansired"),
            "prompt_bg": str(data.get("prompt_bg") or ""),
            "prompt_prefix_color": str(data.get("prompt_prefix_color") or "1;32"),
        })
        return prefs
    except Exception:
        return default_model_prefs()


def serialize_model_prefs(
    hidden_models: List[str],
    speed_tags: Dict[str, str],
    model_usage_counts: Dict[str, int],
    failover_uses: int = 0,
) -> Dict[str, Any]:
    return {
        "hidden_models": sorted(set(hidden_models)),
        "speed_tags": dict(sorted(speed_tags.items())),
        "model_usage_counts": dict(sorted((str(k), int(v)) for k, v in model_usage_counts.items())),
        "failover_uses": max(0, int(failover_uses)),
    }


def save_model_prefs(
    hidden_models: List[str],
    speed_tags: Dict[str, str],
    model_usage_counts: Dict[str, int],
    failover_uses: int,
    disabled_tools: List[str],
    aliases: Dict[str, str],
    last_model: str,
    last_api_account: str,
    system_instruction: str,
    tool_loop_limit: int,
    auto_failover_default: bool = False,
    auto_failover_projects: Optional[Dict[str, bool]] = None,
    api_account_model_prefs: Optional[Dict[str, Dict[str, Any]]] = None,
    prompt_fg: str = "ansired",
    prompt_bg: str = "",
    prompt_prefix_color: str = "1;32",
) -> str:
    account_model_prefs = serialize_model_prefs(hidden_models, speed_tags, model_usage_counts, failover_uses)
    api_accounts = {
        str(account_name): {"failover_uses": max(0, int(account_prefs.get("failover_uses", 0) or 0))}
        for account_name, account_prefs in (api_account_model_prefs or {}).items()
    }
    if last_api_account:
        api_accounts[last_api_account] = {"failover_uses": max(0, int(failover_uses))}
    payload = {
        **account_model_prefs,
        "api_accounts": dict(sorted(api_accounts.items())),
        "disabled_tools": sorted(set(disabled_tools)),
        "aliases": dict(sorted(aliases.items())),
        "last_model": last_model,
        "last_api_account": last_api_account,
        "system_instruction": system_instruction,
        "tool_loop_limit": int(tool_loop_limit),
        "auto_failover_default": bool(auto_failover_default),
        "auto_failover_projects": dict(sorted((str(k), bool(v)) for k, v in (auto_failover_projects or {}).items())),
        "prompt_fg": prompt_fg,
        "prompt_bg": prompt_bg,
        "prompt_prefix_color": prompt_prefix_color,
    }
    MODEL_PREFS_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"Saved model preferences to {MODEL_PREFS_FILE}"


def load_api_accounts(password: Optional[str] = None) -> Dict[str, Any]:
    if API_ACCOUNTS_FILE.exists():
        if password is None:
            password = _prompt_password("Load API accounts")
        if not password:
            raise RuntimeError("Password is required to load API accounts.")
        try:
            return _decrypt_api_accounts(API_ACCOUNTS_FILE.read_bytes(), password)
        except Exception as exc:
            raise RuntimeError(f"Could not load locked API accounts: {exc}") from exc

    if API_ACCOUNTS_LEGACY_FILE.exists():
        try:
            data = json.loads(API_ACCOUNTS_LEGACY_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Legacy API account file is invalid.")
            accounts = data.get("accounts", {})
            if not isinstance(accounts, dict):
                accounts = {}
            tavily_accounts = data.get("tavily_accounts", {})
            if not isinstance(tavily_accounts, dict):
                tavily_accounts = {}
            normalized = {str(name): str(key) for name, key in accounts.items()}
            normalized_tavily = {str(name): str(key) for name, key in tavily_accounts.items()}
        except Exception as exc:
            raise RuntimeError(f"Could not read legacy API accounts: {exc}") from exc
        if password is None:
            password = _prompt_password("Lock API accounts")
        if not password:
            raise RuntimeError("Password is required to lock API accounts.")
        API_ACCOUNTS_FILE.write_bytes(_encrypt_api_accounts(normalized, password, normalized_tavily))
        try:
            API_ACCOUNTS_LEGACY_FILE.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            pass
        return {"accounts": normalized, "tavily_accounts": normalized_tavily}

    return {"accounts": {}, "tavily_accounts": {}}


def save_api_accounts(
    accounts: Dict[str, str],
    password: Optional[str] = None,
    tavily_accounts: Optional[Dict[str, str]] = None,
) -> str:
    if password is None:
        password = _prompt_password("Save API accounts")
    if not password:
        return "Error: password is required."
    try:
        API_ACCOUNTS_FILE.write_bytes(_encrypt_api_accounts(accounts, password, tavily_accounts or {}))
        try:
            API_ACCOUNTS_LEGACY_FILE.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            pass
    except Exception as exc:
        return f"Error saving locked API accounts: {exc}"
    return f"Saved locked API accounts to {API_ACCOUNTS_FILE}"


def clear_screen() -> None:
    if sys.stdout.isatty():
        if os.name == "nt":
            os.system("cls")
        else:
            sys.stdout.write("\033[3J\033[2J\033[H")
            sys.stdout.flush()


def read_key() -> str:
    if msvcrt is None:
        return input().strip()
    ch = msvcrt.getwch()
    if ch in ("\x00", "\xe0"):
        ch2 = msvcrt.getwch()
        return ch + ch2
    return ch


def _get_term_height() -> int:
    try:
        return os.get_terminal_size().lines
    except Exception:
        return 24


def interactive_select(
    title_text: str,
    items: List[Dict[str, Any]],
    render_item,
    header_lines: Optional[List[str]] = None,
    footer_lines: Optional[List[str]] = None,
    dynamic_footer: Optional[Callable[[Dict[str, Any]], List[str]]] = None,
    instructions: str = "Use Up/Down to choose, Enter to select, Esc to cancel.",
    on_space: Optional[Callable[[Dict[str, Any], int], None]] = None,
    on_key: Optional[Callable[[str, List[Dict[str, Any]], int], Optional[str]]] = None,
) -> Optional[Dict[str, Any]]:
    if not items:
        return None
    index = 0
    top_index = 0
    footer_lines = footer_lines or []

    while True:
        if not items:
            return None
        index = max(0, min(index, len(items) - 1))

        term_h = _get_term_height()
        title_count = 1 if title_text else 0
        inst_count = 2 if instructions else 0
        header_count = len(header_lines) if header_lines else 0
        sample_footer = dynamic_footer(items[index]) if dynamic_footer else footer_lines
        footer_count = (len(sample_footer) + 1) if sample_footer else 0

        fixed_overhead = title_count + inst_count + header_count + footer_count + 2
        max_visible = max(3, term_h - fixed_overhead)

        if index < top_index:
            top_index = index
        elif index >= top_index + max_visible:
            top_index = index - max_visible + 1

        top_index = max(0, min(top_index, max(0, len(items) - max_visible)))
        visible_slice = items[top_index : top_index + max_visible]

        clear_screen()
        if title_text:
            title(title_text)
        if instructions:
            print(instructions)
            print()

        if header_lines:
            for line in header_lines:
                print(line)

        for relative_i, item in enumerate(visible_slice):
            actual_i = top_index + relative_i
            line = render_item(item, actual_i, actual_i == index)
            print(line)

        if len(items) > max_visible:
            more_above = top_index
            more_below = len(items) - (top_index + len(visible_slice))
            scroll_info = []
            if more_above > 0:
                scroll_info.append(f"▲ {more_above} above")
            if more_below > 0:
                scroll_info.append(f"▼ {more_below} below")
            scroll_str = f"  [{index + 1}/{len(items)}]"
            if scroll_info:
                scroll_str += "  (" + ", ".join(scroll_info) + ")"
            print(_ansi_wrap(scroll_str, "90"))

        current_footer = dynamic_footer(items[index]) if dynamic_footer else footer_lines
        if current_footer:
            print()
            for line in current_footer:
                print(line)

        key = read_key()
        if key in ("\r", "\n"):
            return items[index]
        if key == "\x1b":
            return None
        if key in ("\xe0H", "\x00H"):
            index = (index - 1) % len(items)
        elif key in ("\xe0P", "\x00P"):
            index = (index + 1) % len(items)
        elif key in ("\xe0I", "\x00I"):
            index = max(0, index - max_visible)
        elif key in ("\xe0Q", "\x00Q"):
            index = min(len(items) - 1, index + max_visible)
        elif key == " " and on_space is not None:
            on_space(items[index], index)
        elif on_key is not None:
            res = on_key(key, items, index)
            if res == "deleted":
                if not items:
                    return None
                index = max(0, min(index, len(items) - 1))
        elif key.lower() == "q":
            return None


def pick_model_interactive(
    models: List[Dict[str, Any]],
    current_model: str,
    title_text: str = "Select Model",
    model_cooldowns: Optional[Dict[str, dt.datetime]] = None,
) -> Optional[str]:
    model_cooldowns = model_cooldowns or {}
    decorated_models: List[Dict[str, Any]] = []
    for model in models:
        copy_model = dict(model)
        copy_model["_state"] = format_cooldown_until(model_cooldowns.get(model_name(model)))
        decorated_models.append(copy_model)
    widths = build_model_table_widths(decorated_models)

    def render_item(model: Dict[str, Any], index: int, selected: bool = False) -> str:
        return format_model_entry(
            index + 1,
            model,
            current_model,
            widths=widths,
            selected=selected,
        )

    chosen = interactive_select(
        title_text="",
        items=decorated_models,
        render_item=render_item,
        header_lines=build_model_table_header(widths),
        dynamic_footer=None,
        footer_lines=["  Use Up/Down to choose, Enter to select, Esc/Q to cancel."],
        instructions="",
    )
    if not chosen:
        return None
    return model_name(chosen)


def build_tool_table_widths(tools: List[Dict[str, Any]]) -> Dict[str, int]:
    name_width = 0
    for tool in tools:
        name_width = max(name_width, len(str(tool.get("name", ""))))
    return {
        "name": min(max(name_width, 10), 30),
    }


def build_tool_table_header(widths: Dict[str, int]) -> List[str]:
    return [
        f"  {'Id':>2}  {'Tool':<{widths['name']}}  State",
        f"  {'--':>2}  {'-' * widths['name']}  -----",
    ]


def format_tool_entry(
    index: int,
    tool: Dict[str, Any],
    widths: Dict[str, int],
    selected: bool = False,
) -> str:
    if tool.get("_is_category"):
        marker = ">" if selected else " "
        title_str = f"=== {tool['category']} ({tool['enabled_count']}/{tool['total_count']} active) ==="
        row = f"{marker} {index:>2}  {title_str}"
        if selected:
            return _ansi_wrap(row, "48;5;24;97")
        return _ansi_wrap(row, "1;36")

    name = str(tool.get("name", ""))
    enabled = bool(tool.get("enabled", True))
    marker = ">" if selected else " "
    state = "on" if enabled else "off"
    state_text = _ansi_wrap(state, "31") if not enabled else _ansi_wrap(state, "32")

    row = (
        f"{marker} {index:>2}  "
        f"{name:<{widths['name']}}  "
        f"{state_text}"
    ).rstrip()
    if selected:
        return _ansi_wrap(row, "48;5;24;97")
    if not enabled:
        return _ansi_wrap(row, "31")
    return row


def pick_tool_interactive(disabled_tools: Set[str], title_text: str = "Manage Tools") -> bool:
    disabled = set(disabled_tools)

    def open_category_picker(cat_name: str) -> bool:
        cat_tools: List[Dict[str, Any]] = []
        for tool in list_tool_catalog():
            if tool.get("category") == cat_name:
                tool_copy = dict(tool)
                tool_copy["enabled"] = tool_copy["name"] not in disabled
                cat_tools.append(tool_copy)

        if not cat_tools:
            return False

        widths = build_tool_table_widths(cat_tools)
        cat_changed = False

        def render_cat_item(tool: Dict[str, Any], index: int, selected: bool = False) -> str:
            return format_tool_entry(index + 1, tool, widths, selected=selected)

        def toggle_cat_tool(tool: Dict[str, Any], _: int) -> None:
            nonlocal cat_changed
            name = str(tool.get("name", ""))
            if bool(tool.get("enabled", True)):
                disabled.add(name)
                tool["enabled"] = False
            else:
                disabled.discard(name)
                tool["enabled"] = True
            cat_changed = True

        def render_footer_info(current_item: Dict[str, Any]) -> List[str]:
            desc = str(current_item.get("description", ""))
            rating = str(current_item.get("rating", ""))
            lines = [
                "----------------------------------------------------------------",
                f"Info: {desc}",
            ]
            if rating:
                lines.append(f"Advice: {rating}")
            lines.append("Press Space to toggle | Enter/Esc to return to Category Menu")
            return lines

        interactive_select(
            title_text=f"Manage Tools -> {cat_name}",
            items=cat_tools,
            render_item=render_cat_item,
            header_lines=build_tool_table_header(widths),
            dynamic_footer=render_footer_info,
            instructions="Use Up/Down to navigate tools, Space to toggle on/off.",
            on_space=toggle_cat_tool,
        )
        return cat_changed

    overall_changed = False
    while True:
        categories_order = ["Code Modifications", "Inspection & File System", "Execution & Shell", "Control Flow"]
        seen = set(categories_order)
        for tool in list_tool_catalog():
            cat = str(tool.get("category", ""))
            if cat and cat not in seen:
                categories_order.append(cat)
                seen.add(cat)
        categories = categories_order
        category_items: List[Dict[str, Any]] = []
        for cat in categories:
            cat_all = [t for t in list_tool_catalog() if t.get("category") == cat]
            enabled_count = sum(1 for t in cat_all if t["name"] not in disabled)
            category_items.append({
                "_is_category": True,
                "category": cat,
                "enabled_count": enabled_count,
                "total_count": len(cat_all),
            })

        def render_main_item(item: Dict[str, Any], index: int, selected: bool = False) -> str:
            return format_tool_entry(index + 1, item, {}, selected=selected)

        chosen_cat = interactive_select(
            title_text=title_text,
            items=category_items,
            render_item=render_main_item,
            header_lines=["  Select a Category to manage its tools:"],
            footer_lines=["Press Enter to open category. Press Esc or Q to finish."],
            instructions="Use Up/Down, Enter to select category, Esc to close.",
        )
        if not chosen_cat:
            break

        cat_name = str(chosen_cat.get("category", ""))
        if cat_name:
            if open_category_picker(cat_name):
                overall_changed = True

    disabled_tools.clear()
    disabled_tools.update(disabled)
    return overall_changed


def test_all_models(client: GeminiClient, models: List[Dict[str, Any]]) -> List[str]:
    speed_tags: Dict[str, str] = {}
    failed_models: List[str] = []
    passed_models: List[str] = []
    passed = 0
    failed = 0
    print()
    title("Testing Models")
    for model in models:
        name = model_name(model)
        print(f"- {short_model_name(model)} [{name}] ... ", end="", flush=True)
        started = time.perf_counter()
        try:
            result = test_model(client, name, temperature=0.0)
            if normalize_text(result).strip() != "OK":
                raise RuntimeError(f"Unexpected response: {result}")
            elapsed = time.perf_counter() - started
            speed_tag = classify_test_speed(elapsed)
            speed_tags[name] = speed_tag
            passed += 1
            passed_models.append(name)
            print(f"OK [{speed_tag}] ({result[:60]})")
        except Exception as exc:
            elapsed = time.perf_counter() - started
            speed_tag = classify_test_speed(elapsed)
            speed_tags[name] = speed_tag
            failed += 1
            failed_models.append(name)
            print(f"FAIL [{speed_tag}] ({exc})")
    print()
    info(f"Test summary: {passed} passed, {failed} failed.")
    test_all_models.last_speed_tags = speed_tags
    test_all_models.last_passed_models = passed_models
    return failed_models


def build_api_account_table_widths(items: List[Dict[str, Any]]) -> Dict[str, int]:
    provider_width = 0
    name_width = 0
    key_width = 0
    failover_width = 0
    for item in items:
        provider_width = max(provider_width, len(str(item.get("provider", ""))))
        name_width = max(name_width, len(str(item.get("name", ""))))
        key_width = max(key_width, len(str(item.get("masked_key", ""))))
        failover_width = max(failover_width, len(str(item.get("failover_uses", ""))))
    return {
        "provider": min(max(provider_width, 8), 12),
        "name": min(max(name_width, 10), 28),
        "key": min(max(key_width, 10), 24),
        "failover": min(max(failover_width, 8), 10),
    }


def build_api_account_table_header(widths: Dict[str, int]) -> List[str]:
    return [
        f"  {'Id':>2}  {'Provider':<{widths['provider']}}  {'Account':<{widths['name']}}  {'Key':<{widths['key']}}  {'Failovers':<{widths['failover']}}  State",
        f"  {'--':>2}  {'-' * widths['provider']}  {'-' * widths['name']}  {'-' * widths['key']}  {'-' * widths['failover']}  -----",
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
    failover_uses = item.get("failover_uses", "")
    failover_text = f"{int(failover_uses)}x" if str(failover_uses).strip() != "" else ""
    state = str(item.get("state", ""))
    marker = ">" if selected else " "
    row = (
        f"{marker} {index:>2}  "
        f"{provider:<{widths['provider']}}  "
        f"{name:<{widths['name']}}  "
        f"{key:<{widths['key']}}  "
        f"{failover_text:<{widths['failover']}}  "
        f"{state}"
    ).rstrip()
    if selected:
        return _ansi_wrap(row, "48;5;24;97")
    if action == "add":
        return _ansi_wrap(row, "32")
    return row


def pick_api_account_interactive(
    accounts: Dict[str, str],
    tavily_accounts: Optional[Dict[str, str]] = None,
    active_api_account: str = "",
    api_account_model_prefs: Optional[Dict[str, Dict[str, Any]]] = None,
    title_text: str = "Manage API Accounts",
) -> Optional[Dict[str, str]]:
    tavily_accounts = tavily_accounts or {}
    api_account_model_prefs = api_account_model_prefs or {}
    items: List[Dict[str, str]] = [{
        "action": "add",
        "provider": "gemini",
        "name": "Add Gemini API",
        "masked_key": "",
        "failover_uses": "",
        "state": "new",
    }, {
        "action": "add",
        "provider": "tavily",
        "name": "Add Tavily API",
        "masked_key": "",
        "failover_uses": "",
        "state": "new",
    }]
    for name, key in sorted(accounts.items(), key=lambda item: item[0].lower()):
        masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
        state = "active" if name == active_api_account else ""
        items.append({
            "action": "load",
            "provider": "gemini",
            "name": name,
            "masked_key": masked,
            "failover_uses": int(normalize_account_model_prefs(api_account_model_prefs.get(name, {})).get("failover_uses", 0) or 0),
            "state": state,
        })
    for name, key in sorted(tavily_accounts.items(), key=lambda item: item[0].lower()):
        masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
        items.append({
            "action": "load",
            "provider": "tavily",
            "name": name,
            "masked_key": masked,
            "failover_uses": "",
            "state": "saved",
        })
    widths = build_api_account_table_widths(items)

    def render_item(item: Dict[str, Any], _: int, selected: bool = False) -> str:
        return format_api_account_entry(_ + 1, item, widths, selected=selected)

    chosen = interactive_select(
        title_text=title_text,
        items=items,
        render_item=render_item,
        header_lines=build_api_account_table_header(widths),
        footer_lines=["Press Q or Esc to cancel."],
    )
    if not chosen:
        return None
    return {
        "action": str(chosen["action"]),
        "provider": str(chosen["provider"]),
        "name": str(chosen["name"]),
    }


def build_failover_table_widths(items: List[Dict[str, Any]]) -> Dict[str, int]:
    scope_width = 0
    state_width = 0
    desc_width = 0
    for item in items:
        scope_width = max(scope_width, len(str(item.get("scope", ""))))
        state_width = max(state_width, len(str(item.get("state", ""))))
        desc_width = max(desc_width, len(str(item.get("description", ""))))
    return {
        "scope": min(max(scope_width, 14), 28),
        "state": min(max(state_width, 7), 12),
        "description": min(max(desc_width, 28), 60),
    }


def build_failover_table_header(widths: Dict[str, int]) -> List[str]:
    return [
        f"  {'Id':>2}  {'Scope':<{widths['scope']}}  {'State':<{widths['state']}}  Description",
        f"  {'--':>2}  {'-' * widths['scope']}  {'-' * widths['state']}  {'-' * 11}",
    ]


def format_failover_entry(
    index: int,
    item: Dict[str, Any],
    widths: Dict[str, int],
    selected: bool = False,
) -> str:
    scope = str(item.get("scope", ""))
    state = str(item.get("state", ""))
    description = str(item.get("description", ""))
    marker = ">" if selected else " "
    state_text = state
    if state == "on":
        state_text = _ansi_wrap(state, "32")
    elif state == "off":
        state_text = _ansi_wrap(state, "31")
    elif state in {"inherit", "none"}:
        state_text = _ansi_wrap(state, "33")
    row = (
        f"{marker} {index:>2}  "
        f"{scope:<{widths['scope']}}  "
        f"{state_text:<{widths['state']}}  "
        f"{description}"
    ).rstrip()
    if selected:
        return _ansi_wrap(row, "48;5;24;97")
    return row


def pick_failover_interactive(
    current_project_state: Optional[bool],
    session_state: Optional[bool],
    global_default_state: bool,
    title_text: str = "Auto Failover",
) -> Optional[Dict[str, Any]]:
    items: List[Dict[str, Any]] = [
        {
            "kind": "project",
            "scope": "Current project",
            "state": "inherit" if current_project_state is None else ("on" if current_project_state else "off"),
            "description": "Persistent override for the current project root.",
        },
        {
            "kind": "session",
            "scope": "This session",
            "state": "none" if session_state is None else ("on" if session_state else "off"),
            "description": "Temporary override until the CLI exits.",
        },
        {
            "kind": "default",
            "scope": "Global default",
            "state": "on" if global_default_state else "off",
            "description": "Fallback when no project override exists.",
        },
    ]
    widths = build_failover_table_widths(items)
    changed = False

    def render_item(item: Dict[str, Any], index: int, selected: bool = False) -> str:
        return format_failover_entry(index + 1, item, widths, selected=selected)

    def toggle_item(item: Dict[str, Any], _: int) -> None:
        nonlocal changed
        kind = str(item.get("kind", ""))
        if kind in {"project", "session", "default"}:
            item["state"] = "on" if str(item.get("state", "")) != "on" else "off"
            changed = True

    chosen = interactive_select(
        title_text=title_text,
        items=items,
        render_item=render_item,
        header_lines=build_failover_table_header(widths),
        footer_lines=[
            "Press Space to toggle the highlighted scope.",
            "Press Enter or Esc to close.",
        ],
        instructions="Use Up/Down, Space to toggle, Enter to close, Esc to cancel.",
        on_space=toggle_item,
    )
    if chosen is None and not changed:
        return None

    result = {
        "project": "inherit" if current_project_state is None else ("on" if current_project_state else "off"),
        "session": "none" if session_state is None else ("on" if session_state else "off"),
        "default": "on" if global_default_state else "off",
    }
    for item in items:
        kind = str(item.get("kind", ""))
        state = str(item.get("state", ""))
        if kind in {"project", "session", "default"}:
            result[kind] = state
    return result


def first_api_account_name(accounts: Dict[str, str]) -> Optional[str]:
    if not accounts:
        return None
    return next(iter(sorted(accounts.keys(), key=str.lower)))


def parse_model_index(text: str) -> Optional[int]:
    try:
        idx = int(text.strip())
    except ValueError:
        return None
    return idx if idx > 0 else None


def model_name(model: Dict[str, Any]) -> str:
    return str(model.get("name", "")).removeprefix("models/")


def short_model_name(model: Dict[str, Any]) -> str:
    name = model_name(model)
    short = name
    for prefix in ("gemini-", "gemma-"):
        if short.startswith(prefix):
            short = short[len(prefix):]
            break
    short = short.replace("-flash-lite", " flash lite")
    short = short.replace("-flash", " flash")
    short = short.replace("-pro", " pro")
    short = short.replace("-", " ")
    return short


def short_model_label(model_name_value: str) -> str:
    short = str(model_name_value or "")
    for prefix in ("gemini-", "gemma-"):
        if short.startswith(prefix):
            short = short[len(prefix):]
            break
    short = short.replace("-flash-lite", " flash lite")
    short = short.replace("-flash", " flash")
    short = short.replace("-pro", " pro")
    short = short.replace("-", " ")
    return short


def model_group(model: Dict[str, Any]) -> str:
    name = model_name(model).lower()
    display_name = str(model.get("displayName") or "").lower()
    if "preview" in name or "preview" in display_name:
        return "Preview"
    if "latest" in name or "latest" in display_name:
        return "Aliases"
    if "gemma" in name or "gemma" in display_name:
        return "Gemma"
    if "image" in name or "banana" in display_name:
        return "Image"
    return "Stable"


def model_is_recommended(model: Dict[str, Any]) -> bool:
    name = model_name(model).lower()
    display_name = str(model.get("displayName") or "").lower()
    if not name.startswith("gemini-"):
        return False
    blocked = (
        "preview",
        "image",
        "tts",
        "robot",
        "computer-use",
        "customtools",
        "omni",
        "gemma",
    )
    if any(token in name or token in display_name for token in blocked):
        return False
    return any(token in name for token in ("flash", "pro"))


def build_model_table_widths(models: List[Dict[str, Any]]) -> Dict[str, int]:
    short_width = 0
    name_width = 0
    tag_width = 0
    state_width = 0
    for model in models:
        short_width = max(short_width, len(short_model_name(model)))
        name_width = max(name_width, len(model_name(model)))
        tag_width = max(tag_width, len(str(model.get("_tag") or "")))
        state_width = max(state_width, len(str(model.get("_state") or "")))
    return {
        "short": min(max(short_width, 12), 28),
        "name": min(max(name_width, 18), 42),
        "tag": min(max(tag_width, 4), 12),
        "state": min(max(state_width, 5), 16),
    }


def build_model_table_header(widths: Dict[str, int]) -> List[str]:
    w_short = widths.get("short", 12)
    w_name = widths.get("name", 18)
    w_tag = widths.get("tag", 4)
    w_state = widths.get("state", 5)

    h_idx = _ansi_wrap(f"{'#':>2}", "1;36")
    h_short = _ansi_wrap(f"{'Model':<{w_short}}", "1;36")
    h_name = _ansi_wrap(f"{'Full Name':<{w_name}}", "1;36")
    h_uses = _ansi_wrap(f"{'Uses':>4}", "1;36")
    h_tag = _ansi_wrap(f"{'Tag':<{w_tag}}", "1;36")
    h_cur = _ansi_wrap("Cur", "1;36")
    h_state = _ansi_wrap(f"{'State':<{w_state}}", "1;36")

    header_str = (
        f"  {h_idx}  "
        f"{h_short}  "
        f"{h_name}  "
        f"{h_uses}  "
        f"{h_tag}  "
        f"{h_cur}  "
        f"{h_state}"
    )

    return [header_str]


def format_model_entry(
    index: int,
    model: Dict[str, Any],
    current_model: str,
    widths: Optional[Dict[str, int]] = None,
    selected: bool = False,
) -> str:
    name = model_name(model)
    display_name = short_model_name(model)
    widths = widths or build_model_table_widths([model])
    active = "*" if name == current_model else " "
    hidden = "hidden" if model.get("_hidden") else ""
    tag = str(model.get("_tag") or "")
    usage = int(model.get("_uses") or 0)
    state = str(model.get("_state") or hidden)
    if state and state != "hidden":
        state = _ansi_wrap(state, "31")
    marker = ">" if selected else " "
    row = (
        f"{marker} {index:>2}  "
        f"{display_name:<{widths['short']}}  "
        f"{name:<{widths['name']}}  "
        f"{usage:>4}  "
        f"{tag:<{widths['tag']}}  "
        f"{active}  "
        f"{state:<{widths['state']}}"
    ).rstrip()
    if selected:
        return _ansi_wrap(row, "48;5;24;97")
    if name == current_model:
        return _ansi_wrap(row, "32")
    if model.get("_hidden"):
        return _ansi_wrap(row, "2")
    return row


def apply_model_tags(
    models: List[Dict[str, Any]],
    speed_tags: Dict[str, str],
    usage_counts: Optional[Dict[str, int]] = None,
) -> List[Dict[str, Any]]:
    tagged_models: List[Dict[str, Any]] = []
    for model in models:
        copy_model = dict(model)
        tag = speed_tags.get(model_name(model))
        if tag:
            copy_model["_tag"] = tag
        if usage_counts is not None:
            uses = int(usage_counts.get(model_name(model), 0) or 0)
            copy_model["_uses"] = uses
        tagged_models.append(copy_model)
    return tagged_models


def classify_test_speed(elapsed_seconds: float) -> str:
    if elapsed_seconds <= 0.5:
        return "fast"
    if 3.0 <= elapsed_seconds <= 5.0:
        return "medium"
    if elapsed_seconds > 6.0:
        return "slow"
    return "normal"


def choose_model_from_list(models: List[Dict[str, Any]], selection: str) -> Optional[str]:
    idx = parse_model_index(selection)
    if idx is not None:
        if 1 <= idx <= len(models):
            return model_name(models[idx - 1])
        return None

    target = selection.strip()
    if not target:
        return None

    for model in models:
        name = model_name(model)
        display_name = str(model.get("displayName", ""))
        if target == name or target == display_name or target == short_model_name(model):
            return name
    return target


def list_chat_models(client: GeminiClient) -> List[Dict[str, Any]]:
    raw_models = client.list_models()
    chat_models: List[Dict[str, Any]] = []
    for model in raw_models:
        name = str(model.get("name", ""))
        methods = model.get("supportedGenerationMethods") or []
        if methods and "generateContent" not in methods:
            continue
        if name and not (name.startswith("models/gemini") or name.startswith("models/gemma")):
            continue
        chat_models.append(model)
    chat_models.sort(key=lambda m: (model_group(m), str(m.get("displayName") or m.get("name") or "").lower()))
    return chat_models


def filter_models_for_display(
    models: List[Dict[str, Any]],
    hidden_models: List[str],
    show_all: bool = False,
) -> List[Dict[str, Any]]:
    hidden = set(hidden_models)
    if show_all:
        shown = []
        for model in models:
            copy_model = dict(model)
            copy_model["_hidden"] = model_name(model) in hidden
            shown.append(copy_model)
        return shown
    return [model for model in models if model_is_recommended(model) and model_name(model) not in hidden]


def test_model(client: GeminiClient, model_name_value: str, temperature: float = 0.0) -> str:
    test_client = GeminiClient(client.api_key, model_name_value)
    response = test_client.generate(
        contents=[make_user_content("Reply with exactly: OK")],
        system_instruction="Reply with exactly OK.",
        tool_names=[],
        temperature=temperature,
        max_output_tokens=16,
    )
    candidates = response.get("candidates", [])
    if not candidates:
        return "Error: model returned no candidates."
    parts = candidates[0].get("content", {}).get("parts", [])
    text = render_model_parts(parts)
    return text or "OK"


def print_help() -> None:
    print(
        textwrap.dedent(
            """
            Commands:
              /help                 Show this message
              /exit                 Quit
              /reset                Clear conversation history
              /mm                   Open the model picker
              /test                 Test all models and hide failures
              /api                  Open the API account picker
              /loops <n>            Set max tool-call loops
              /failover             Open the auto-failover picker
              /tool                 Open the tool manager and toggle tools with Space
              /system <text|file>   Replace system instruction or load it from a file
              /skill                Browse and apply saved skill instructions
              /resume, /r [file]    Resume a recent conversation session
              /tokens               Show estimated conversation token count
              /run                  Execute code blocks from last AI response
              /alias                Manage custom prompt macros/shortcuts
              /save <file>          Save transcript JSON
              /load <file>          Load transcript JSON
            """
        ).strip()
    )


def _get_term_width() -> int:
    try:
        return os.get_terminal_size().columns
    except Exception:
        return 90


def format_relative_time(mtime: float) -> str:
    diff = max(0, int(time.time() - mtime))
    if diff < 60:
        return f"{diff}s ago"
    minutes = diff // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    rem_m = minutes % 60
    if hours < 24:
        return f"{hours}h {rem_m}m" if rem_m > 0 else f"{hours}h ago"
    days = hours // 24
    rem_h = hours % 24
    if days < 30:
        return f"{days}d {rem_h}h" if rem_h > 0 else f"{days}d ago"
    months = days // 30
    if months < 12:
        return f"{months}mo ago"
    years = days // 365
    return f"{years}y ago"


def list_recent_transcripts(limit: int = 100) -> List[Dict[str, Any]]:
    """Scan transcripts directory and return a list of metadata for recent sessions."""
    if not TRANSCRIPTS_DIR.exists():
        return []

    transcripts: List[Dict[str, Any]] = []
    for path in TRANSCRIPTS_DIR.glob("*.json"):
        try:
            mtime = path.stat().st_mtime
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            if not isinstance(data, dict) or "contents" not in data:
                continue
            contents = data.get("contents", [])
            if not contents:
                continue

            first_prompt = ""
            user_msg_count = 0
            for msg in contents:
                if msg.get("role") == "user":
                    parts = msg.get("parts", [])
                    is_user_text = False
                    for p in parts:
                        if "text" in p:
                            is_user_text = True
                            if not first_prompt:
                                raw = str(p["text"]).strip()
                                first_prompt = re.sub(r"\s+", " ", raw)
                    if is_user_text:
                        user_msg_count += 1

            if not first_prompt:
                first_prompt = "<No user text>"

            tool_call_count = 0
            for msg in contents:
                for p in msg.get("parts", []):
                    if isinstance(p, dict) and "functionCall" in p:
                        tool_call_count += 1

            model = str(data.get("model", "unknown"))
            project_root = str(data.get("project_root", ""))
            rel_time = format_relative_time(mtime)
            full_dt = dt.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

            custom_title = data.get("custom_title")
            display_title = str(custom_title).strip() if custom_title else first_prompt

            transcripts.append({
                "path": path,
                "mtime": mtime,
                "date_str": rel_time,
                "full_date": full_dt,
                "model": model,
                "project_root": project_root,
                "msg_count": max(1, user_msg_count),
                "tool_count": tool_call_count,
                "first_prompt": display_title[:150],
                "data": data,
            })
        except Exception:
            continue

    transcripts.sort(key=lambda x: x["mtime"], reverse=True)
    return transcripts[:limit]


def build_transcript_table_widths(transcripts: List[Dict[str, Any]]) -> Dict[str, int]:
    folder_width = 0
    msg_width = 0
    tool_width = 0
    for item in transcripts:
        p_root = item.get("project_root", "")
        folder_s = Path(p_root).name if p_root else ""
        folder_width = max(folder_width, len(folder_s))
        msg_s = str(item["msg_count"])
        msg_width = max(msg_width, len(msg_s))
        tool_s = str(item.get("tool_count", 0))
        tool_width = max(tool_width, len(tool_s))
    return {
        "folder": min(max(folder_width, 6), 16),
        "msg": min(max(msg_width, 4), 6),
        "tool": min(max(tool_width, 5), 6),
    }


def build_transcript_table_header(widths: Dict[str, int]) -> List[str]:
    w_folder = widths.get("folder", 12)
    w_msg = widths.get("msg", 4)
    w_tool = widths.get("tool", 5)

    h_idx = _ansi_wrap(f"{'#':>2}.", "1;36")
    h_age = _ansi_wrap(f"{'Age':<10}", "1;36")
    h_folder = _ansi_wrap(f"{'Folder':<{w_folder}}", "1;36")
    h_msg = _ansi_wrap(f"{'Msgs':>{w_msg}}", "1;36")
    h_tool = _ansi_wrap(f"{'Tools':>{w_tool}}", "1;36")
    h_prompt = _ansi_wrap("First Prompt", "1;36")

    header_str = (
        f"  {h_idx} "
        f"{h_age}  "
        f"{h_folder}  "
        f"{h_msg}  "
        f"{h_tool}  "
        f"{h_prompt}"
    )

    return [header_str]


def format_transcript_entry(
    index: int,
    item: Dict[str, Any],
    widths: Dict[str, int],
    selected: bool = False,
) -> str:
    date_s = item["date_str"][:10]
    p_root = item.get("project_root", "")
    folder_s = Path(p_root).name if p_root else ""
    msg_s = str(item["msg_count"])
    tools_s = str(item.get("tool_count", 0))
    prompt_s = item["first_prompt"]

    w_folder = widths["folder"]
    w_msg = widths["msg"]
    w_tool = widths["tool"]

    folder_s = folder_s[:w_folder]
    msg_s = msg_s[:w_msg]
    tools_s = tools_s[:w_tool]

    marker = ">" if selected else " "

    term_w = _get_term_width()
    prefix_len = 6 + 10 + 2 + w_folder + 2 + w_msg + 2 + w_tool + 2
    avail_prompt_len = term_w - prefix_len - 1

    if avail_prompt_len < 10:
        avail_prompt_len = 10

    if len(prompt_s) > avail_prompt_len:
        if avail_prompt_len > 3:
            prompt_s = prompt_s[:avail_prompt_len - 3] + ".."
        else:
            prompt_s = prompt_s[:avail_prompt_len]

    row = (
        f"{marker} {index:>2}. "
        f"{date_s:<10}  "
        f"{folder_s:<{w_folder}}  "
        f"{msg_s:>{w_msg}}  "
        f"{tools_s:>{w_tool}}  "
        f"{prompt_s}"
    )

    if selected:
        return _ansi_wrap(row, "48;5;24;97")
    return row


def pick_transcript_interactive(client: Optional[GeminiClient] = None) -> Optional[Dict[str, Any]]:
    items = list_recent_transcripts()
    if not items:
        warn("No recent transcripts found in 'transcripts/' directory.")
        return None

    widths = build_transcript_table_widths(items)

    def render_item(item: Dict[str, Any], index: int, selected: bool = False) -> str:
        return format_transcript_entry(index + 1, item, widths, selected=selected)

    def render_footer_info(current_item: Dict[str, Any]) -> List[str]:
        p_root = current_item.get("project_root") or "Not set"
        term_w = _get_term_width()
        divider_len = min(term_w - 2, 80)
        divider = _ansi_wrap("─" * divider_len, "90")

        prompt = current_item["first_prompt"]
        max_p_len = max(10, term_w - 14)
        if len(prompt) > max_p_len:
            prompt = prompt[:max_p_len - 3] + "..."

        saved_date = current_item.get("full_date", current_item["date_str"])
        model_s = short_model_label(current_item["model"])[:18]
        file_name = current_item["path"].name[:28]
        msgs_str = str(current_item["msg_count"])[:3]
        tools_str = str(current_item.get("tool_count", 0))[:3]
        p_root_fixed = p_root[:35]

        lbl_file = _ansi_wrap("📁 File:", "1;36")
        val_file = _ansi_wrap(f"{file_name:<28}", "97")

        lbl_root = _ansi_wrap("📍 Root:", "1;36")
        val_root = _ansi_wrap(f"{p_root_fixed:<35}", "90")

        lbl_model = _ansi_wrap("🤖 Model:", "1;35")
        val_model = _ansi_wrap(f"{model_s:<18}", "1;37")

        lbl_turns = _ansi_wrap("💬 Turns:", "1;33")
        val_turns = _ansi_wrap(f"{msgs_str:>3}", "97")

        lbl_tools = _ansi_wrap("🛠️ Tools:", "1;32")
        val_tools = _ansi_wrap(f"{tools_str:>3}", "97")

        lbl_saved = _ansi_wrap("🕒 Saved:", "1;34")
        val_saved = _ansi_wrap(f"{saved_date:<16}", "90")

        lbl_prompt = _ansi_wrap("💡 Prompt:", "1;36")
        val_prompt = _ansi_wrap(prompt, "38;5;214")

        sep = _ansi_wrap("•", "36")

        b_enter = f"\033[48;5;24;97m [Enter] \033[0m {_ansi_wrap('Resume & cd', '1;36')}"
        b_del = f"\033[48;5;52;97m [d] \033[0m {_ansi_wrap('Delete', '1;31')}"
        b_ren = f"\033[48;5;240;97m [r] \033[0m {_ansi_wrap('Rename', '1;33')}"
        b_gen = f"\033[48;5;28;97m [g] \033[0m {_ansi_wrap('AI Title', '1;32')}"
        b_esc = f"\033[48;5;238;97m [Esc/Q] \033[0m {_ansi_wrap('Cancel', '90')}"

        return [
            divider,
            f"  {lbl_file} {val_file}  {sep}  {lbl_root} {val_root}",
            f"  {lbl_model} {val_model}  {sep}  {lbl_turns} {val_turns}  {sep}  {lbl_tools} {val_tools}  {sep}  {lbl_saved} {val_saved}",
            f"  {lbl_prompt} {val_prompt}",
            f"  {b_enter}  {sep}  {b_del}  {sep}  {b_ren}  {sep}  {b_gen}  {sep}  {b_esc}",
        ]

    def handle_key(key: str, items_list: List[Dict[str, Any]], idx: int) -> Optional[str]:
        if key.lower() == "d":
            if 0 <= idx < len(items_list):
                item = items_list[idx]
                try:
                    path = item["path"]
                    if path.exists():
                        path.unlink()
                except Exception:
                    pass
                items_list.pop(idx)
                return "deleted"

        if key.lower() == "r":
            if 0 <= idx < len(items_list):
                item = items_list[idx]
                print()
                curr_t = item.get("data", {}).get("custom_title") or item["first_prompt"]
                new_t = input(f"Enter custom title for {item['path'].name} (current: '{curr_t}'): ").strip()
                if new_t:
                    item["data"]["custom_title"] = new_t
                    item["first_prompt"] = new_t
                    try:
                        save_transcript(item["path"], item["data"])
                        info(f"Updated title to: '{new_t}'")
                    except Exception as exc:
                        error(f"Error saving title: {exc}")
                return "renamed"

        if key.lower() == "g":
            if 0 <= idx < len(items_list):
                item = items_list[idx]
                target_client = client

                if target_client is None:
                    m_prefs = load_model_prefs()
                    cur_m = str(item.get("model") or m_prefs.get("last_model") or DEFAULT_MODEL)
                    
                    # Use active in-memory API key without triggering file decryption password prompt
                    k = globals().get("api_key", "") or os.environ.get("GEMINI_API_KEY", "")
                    if k:
                        target_client = GeminiClient(k, cur_m)

                if target_client is None or not target_client.api_key:
                    print(_ansi_wrap("\n  [Error] No active API key found in memory.", "31"))
                    time.sleep(2)
                    return "error"

                print(_ansi_wrap(f"\n  [AI Title] Generating summary using {target_client.model}...", "36"))

                conv_text = []
                for msg in item.get("data", {}).get("contents", []):
                    role = msg.get("role", "user")
                    parts = msg.get("parts", [])
                    txt_parts = [p["text"] for p in parts if isinstance(p, dict) and "text" in p]
                    if txt_parts:
                        text_str = ' '.join(txt_parts).strip()
                        if text_str:
                            conv_text.append(f"{role}: {text_str}")

                full_conv_summary = "\n".join(conv_text)
                if not full_conv_summary.strip():
                    print(_ansi_wrap("\n  [Warning] Conversation transcript has no text content.", "33"))
                    time.sleep(1.5)
                    return "empty"

                if len(full_conv_summary) > 12000:
                    full_conv_summary = full_conv_summary[:6000] + "\n... [middle omitted] ...\n" + full_conv_summary[-6000:]

                try:
                    title_gen_client = GeminiClient(target_client.api_key, target_client.model)
                    res = title_gen_client.generate(
                        contents=[make_user_content(f"Summarize this conversation into a short title (3 to 6 words). Return ONLY the title text:\n\n{full_conv_summary}")],
                        system_instruction="Reply with ONLY a concise title (3 to 6 words). No quotes, no markdown, no punctuation.",
                        tool_names=[],
                        temperature=0.2,
                        max_output_tokens=25,
                    )
                    cands = res.get("candidates", [])
                    if cands:
                        raw_title = render_model_parts(cands[0].get("content", {}).get("parts", [])).strip()
                        raw_title = re.sub(r'["\'`\.]', '', raw_title).strip()
                        if raw_title:
                            item["data"]["custom_title"] = raw_title
                            item["first_prompt"] = raw_title
                            save_transcript(item["path"], item["data"])
                            print(_ansi_wrap(f"\n  [Success] AI Title generated: '{raw_title}'", "32"))
                            time.sleep(1)
                    else:
                        print(_ansi_wrap("\n  [Warning] Gemini API returned no title candidate.", "33"))
                        time.sleep(2)
                except Exception as exc:
                    print(_ansi_wrap(f"\n  [API Error] Could not generate title: {exc}", "31"))
                    time.sleep(2.5)
                return "generated"

        return None

    chosen = interactive_select(
        title_text="",
        items=items,
        render_item=render_item,
        header_lines=build_transcript_table_header(widths),
        dynamic_footer=render_footer_info,
        instructions="",
        on_key=handle_key,
    )
    if not chosen:
        return None
    return chosen
def list_skills(cwd: Optional[Path] = None) -> List[tuple[str, str, Path]]:
    """Scan CLI skills directory and optional cwd skills directory, returning a list of (title, description, path)."""
    skills_dirs = [SKILLS_DIR]
    if cwd and (cwd / "skills").exists() and (cwd / "skills").resolve() != SKILLS_DIR.resolve():
        skills_dirs.append(cwd / "skills")

    found_skills = []
    seen_names = set()
    for s_dir in skills_dirs:
        if not s_dir.exists() or not s_dir.is_dir():
            continue
        for path in sorted(s_dir.glob("*.md")):
            if path.stem in seen_names:
                continue
            seen_names.add(path.stem)
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                lines = content.splitlines()
                title = path.stem.replace("_", " ").title()
                desc = "Custom skill instruction file."
                
                for line in lines:
                    if line.startswith("# "):
                        title = line[2:].strip()
                        break
                
                for line in lines:
                    if line.startswith("## Goal") or line.startswith("## Description") or line.startswith("Description:"):
                        idx = lines.index(line)
                        if idx + 1 < len(lines):
                            desc = lines[idx + 1].strip()
                        break
                found_skills.append((title, desc, path))
            except Exception:
                continue
    return found_skills


def pick_skill_interactive(cwd: Optional[Path] = None) -> Optional[str]:
    skills = list_skills(cwd=cwd)
    if not skills:
        warn("No skills found in 'skills/' directory.")
        return None
    
    items = []
    for title_str, desc_str, path in skills:
        items.append({
            "name": title_str,
            "description": desc_str,
            "path": path,
        })
    
    def render_skill_item(item: Dict[str, Any], index: int, selected: bool = False) -> str:
        marker = ">" if selected else " "
        title_styled = _ansi_wrap(item["name"], "1;36") if selected else item["name"]
        row = f"{marker} {title_styled}"
        if selected:
            return _ansi_wrap(row, "48;5;24;97")
        return row

    def render_footer_info(current_item: Dict[str, Any]) -> List[str]:
        return [
            "----------------------------------------------------------------",
            f"Skill: {current_item['name']}",
            f"File: {current_item['path'].name}",
            f"Description: {current_item['description']}",
            "Press Enter to load skill instruction into current conversation | Esc to cancel"
        ]

    chosen = interactive_select(
        title_text="Select Skill Instruction",
        items=items,
        render_item=render_skill_item,
        header_lines=["  Choose a skill to load into conversation:"],
        dynamic_footer=render_footer_info,
        instructions="Use Up/Down, Enter to apply skill, Esc to cancel.",
    )
    if not chosen:
        return None
    
    try:
        return chosen["path"].read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        error(f"Error reading skill file: {exc}")
        return None



def make_user_content(text: str) -> Dict[str, Any]:
    return {"role": "user", "parts": [{"text": text}]}


def make_user_content_from_input(user_text: str, cwd: Path) -> Dict[str, Any]:
    stripped = user_text.strip()
    img_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

    if stripped.startswith("@"):
        head, _, tail = stripped[1:].partition(" ")
        file_path = resolve_path(head, cwd)
        if file_path.exists() and file_path.is_file() and file_path.suffix.lower() in img_exts:
            info_msg, inline_part = inspect_image_file(file_path)
            if inline_part:
                req_text = tail.strip() or "Please describe and analyze this image."
                return {
                    "role": "user",
                    "parts": [
                        inline_part,
                        {"text": f"Image: {file_path}\n{info_msg}\n\nUser request: {req_text}"}
                    ]
                }

    # Detect image path anywhere in prompt (e.g. "C:\path\image.png what is this?")
    tokens = stripped.split()
    found_img_path = None
    remaining_tokens = []
    for token in tokens:
        clean_tok = token.strip("\"'")
        if any(clean_tok.lower().endswith(ext) for ext in img_exts):
            cand = resolve_path(clean_tok, cwd)
            if cand.exists() and cand.is_file() and cand.suffix.lower() in img_exts:
                found_img_path = cand
                continue
        remaining_tokens.append(token)

    if found_img_path:
        info_msg, inline_part = inspect_image_file(found_img_path)
        if inline_part:
            req_text = " ".join(remaining_tokens).strip() or "Please describe and analyze this image in detail."
            return {
                "role": "user",
                "parts": [
                    inline_part,
                    {"text": f"Image: {found_img_path}\n{info_msg}\n\nUser request: {req_text}"}
                ]
            }

    expanded = expand_at_file_prompt(user_text, cwd)
    return {"role": "user", "parts": [{"text": expanded}]}


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
        request_text = "Review the file above."

    return (
        f"File: {file_path}\n\n"
        f"Content:\n{file_text}\n\n"
        f"User request: {request_text}"
    )


def resolve_system_instruction_input(text: str, cwd: Path) -> tuple[str, bool]:
    """Returns (content, was_file_found)."""
    # Detect if user is likely trying to provide a path
    is_path_like = any(c in text for c in "/\\") or text.endswith((".md", ".txt"))
    candidate = resolve_path(text, cwd)
    
    if candidate.exists() and candidate.is_file():
        content = read_file(candidate)
        if not content.startswith("Error:"):
            return content, True
            
    return text, not is_path_like


def main() -> int:
    parser = argparse.ArgumentParser(description="Gemini terminal CLI")
    parser.add_argument("startup_args", nargs="*", help="Optional startup command such as /api 09")
    parser.add_argument("-p", "--prompt", help="Run one prompt and exit")
    parser.add_argument("--api-key", default=None, help="Gemini API key")
    parser.add_argument("--password", "--api-password", dest="api_password", default=None, help="Password for locked API accounts")
    parser.add_argument("--model", default=None, help="Gemini model")
    parser.add_argument("--system", default=DEFAULT_SYSTEM, help="System instruction")
    parser.add_argument("--project-root", default=os.getcwd(), help="Working directory for local tools")
    parser.add_argument("--temperature", type=float, default=0.2, help="Generation temperature")
    parser.add_argument("--max-output-tokens", type=int, default=2048, help="Max output tokens")
    parser.add_argument("--max-tool-loops", type=int, default=None, help="Max tool-call loops per turn")
    parser.add_argument("--no-tools", action="store_true", help="Disable local tool calling")
    parser.add_argument("-r", "--resume", nargs="?", const="interactive", help="Resume a recent conversation session")
    parser.add_argument("--load-transcript", help="Load transcript JSON at startup")
    parser.add_argument("--save-transcript", help="Auto-save transcript on exit")
    args = parser.parse_args()

    cwd = resolve_path(args.project_root, Path.cwd())
    if not cwd.exists():
        error(f"Project root does not exist: {cwd}")
        return 1

    model_prefs = load_model_prefs()
    api_account_model_prefs: Dict[str, Dict[str, Any]] = dict(model_prefs.get("api_accounts", {}))
    hidden_models: List[str] = list(model_prefs.get("hidden_models", []))
    speed_tags: Dict[str, str] = dict(model_prefs.get("speed_tags", {}))
    model_usage_counts: Dict[str, int] = dict(model_prefs.get("model_usage_counts", {}))
    disabled_tools: Set[str] = set(str(item) for item in model_prefs.get("disabled_tools", []))
    aliases: Dict[str, str] = dict(model_prefs.get("aliases", {}))
    prompt_fg = str(model_prefs.get("prompt_fg") or "ansired")
    prompt_bg = str(model_prefs.get("prompt_bg") or "")
    prompt_prefix_color = str(model_prefs.get("prompt_prefix_color") or "1;32")
    last_assistant_response_text = ""
    last_turn_tokens: Optional[int] = None
    saved_last_model = str(model_prefs.get("last_model") or DEFAULT_MODEL)
    saved_last_api_account = str(model_prefs.get("last_api_account") or "")
    saved_system_instruction = str(model_prefs.get("system_instruction") or DEFAULT_SYSTEM)
    tool_loop_limit = int(model_prefs.get("tool_loop_limit") or DEFAULT_TOOL_LOOPS)
    auto_failover_default = normalize_bool(model_prefs.get("auto_failover_default", False))
    auto_failover_projects_raw = model_prefs.get("auto_failover_projects", {})
    if not isinstance(auto_failover_projects_raw, dict):
        auto_failover_projects_raw = {}
    auto_failover_projects: Dict[str, bool] = {
        str(project_root): normalize_bool(enabled)
        for project_root, enabled in auto_failover_projects_raw.items()
    }
    if args.max_tool_loops is not None:
        tool_loop_limit = max(1, int(args.max_tool_loops))

    api_accounts: Dict[str, str] = {}
    tavily_accounts: Dict[str, str] = {}
    api_accounts_loaded = False

    def ensure_api_accounts_loaded() -> Dict[str, str]:
        nonlocal api_accounts, tavily_accounts, api_accounts_loaded
        if not api_accounts_loaded:
            try:
                loaded_api_accounts = load_api_accounts(password=args.api_password)
                api_accounts = dict(loaded_api_accounts.get("accounts", {}))
                tavily_accounts = dict(loaded_api_accounts.get("tavily_accounts", {}))
            except RuntimeError as exc:
                error(str(exc))
                api_accounts = {}
                tavily_accounts = {}
                return api_accounts
            api_accounts_loaded = True
        return api_accounts

    def ensure_tavily_accounts_loaded() -> Dict[str, str]:
        ensure_api_accounts_loaded()
        return tavily_accounts

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY", "")
    active_api_account = ""
    active_model = args.model or saved_last_model or DEFAULT_MODEL
    failover_uses = int(model_prefs.get("failover_uses") or 0)
    auto_failover_session_override: Optional[bool] = None
    all_tool_names = tool_name_set()

    def snapshot_active_account_model_prefs() -> None:
        if active_api_account:
            api_account_model_prefs[active_api_account] = {"failover_uses": max(0, int(failover_uses))}

    def load_account_model_prefs(account_name: str) -> None:
        nonlocal failover_uses
        account_prefs = normalize_account_model_prefs(api_account_model_prefs.get(account_name, {}))
        failover_uses = int(account_prefs.get("failover_uses", 0) or 0)

    def switch_api_account(account_name: str, key: str) -> None:
        nonlocal active_api_account, api_key
        snapshot_active_account_model_prefs()
        active_api_account = account_name
        api_key = key
        globals()["api_key"] = key
        load_account_model_prefs(account_name)

    def current_project_key() -> str:
        return str(cwd.resolve())

    def project_auto_failover_enabled() -> bool:
        return auto_failover_projects.get(current_project_key(), auto_failover_default)

    def current_project_auto_failover_state() -> Optional[bool]:
        return auto_failover_projects.get(current_project_key())

    def effective_auto_failover_enabled() -> bool:
        if auto_failover_session_override is not None:
            return auto_failover_session_override
        return project_auto_failover_enabled()

    def auto_failover_source() -> str:
        if auto_failover_session_override is not None:
            return "session"
        if current_project_key() in auto_failover_projects:
            return "project"
        return "default"

    def set_project_auto_failover(enabled: bool) -> None:
        nonlocal auto_failover_session_override
        auto_failover_projects[current_project_key()] = enabled
        auto_failover_session_override = None
        persist_selection()

    def clear_project_auto_failover() -> None:
        nonlocal auto_failover_session_override
        auto_failover_projects.pop(current_project_key(), None)
        auto_failover_session_override = None
        persist_selection()

    def set_session_auto_failover(enabled: Optional[bool]) -> None:
        nonlocal auto_failover_session_override
        auto_failover_session_override = enabled

    def apply_failover_picker_state(selection: Dict[str, str]) -> None:
        nonlocal auto_failover_default
        project_state = str(selection.get("project", "inherit"))
        session_state = str(selection.get("session", "none"))
        default_state = str(selection.get("default", "on"))

        if project_state == "inherit":
            auto_failover_projects.pop(current_project_key(), None)
        elif project_state in {"on", "off"}:
            auto_failover_projects[current_project_key()] = project_state == "on"

        if session_state == "none":
            set_session_auto_failover(None)
        elif session_state in {"on", "off"}:
            set_session_auto_failover(session_state == "on")

        if default_state in {"on", "off"}:
            auto_failover_default = default_state == "on"

        persist_selection()

    def format_auto_failover_status() -> str:
        return "on" if effective_auto_failover_enabled() else "off"

    def failover_status_line() -> str:
        source = auto_failover_source()
        if source == "session":
            scope = "session override"
        elif source == "project":
            scope = "project setting"
        else:
            scope = "global default"
        
        status = format_auto_failover_status()
        if status == "off":
            status = _ansi_wrap(status, "31") # Red
            
        return f"Auto failover: {status} ({scope})"

    if args.no_tools:
        disabled_tools = set(all_tool_names)

    if args.startup_args:
        if args.startup_args[0].startswith("/"):
            startup_command = args.startup_args[0].lower()
            startup_remainder = " ".join(args.startup_args[1:]).strip()
            if startup_command == "/api":
                accounts = ensure_api_accounts_loaded()
                if not accounts:
                    error("No saved API accounts. Use /api first.")
                    return 1
                chosen_name = startup_remainder or first_api_account_name(accounts)
                if not chosen_name or chosen_name not in accounts:
                    error("Unknown API account name.")
                    return 1
                switch_api_account(chosen_name, accounts[chosen_name])
            else:
                warn(f"Ignoring unknown startup command: {' '.join(args.startup_args)}")
        elif not args.prompt:
            args.prompt = " ".join(args.startup_args)

    if not api_key:
        accounts = ensure_api_accounts_loaded()
        if accounts:
            chosen_name = saved_last_api_account if saved_last_api_account in accounts else first_api_account_name(accounts)
            if chosen_name:
                switch_api_account(chosen_name, accounts[chosen_name])

    if not api_key:
        error("Missing Gemini API key. Use /api to add one, or pass --api-key / GEMINI_API_KEY.")
        return 1

    client = GeminiClient(api_key, active_model)
    system_instruction = saved_system_instruction if args.system == DEFAULT_SYSTEM else args.system
    contents: List[Dict[str, Any]] = []
    model_cooldowns: Dict[str, dt.datetime] = {}
    current_session_path: Optional[Path] = None

    def auto_save_session() -> None:
        nonlocal current_session_path
        if not contents:
            return
        if current_session_path is None:
            TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
            current_session_path = TRANSCRIPTS_DIR / f"session_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        state = {
            "model": client.model,
            "system_instruction": system_instruction,
            "project_root": str(cwd),
            "disabled_tools": sorted(disabled_tools),
            "contents": contents,
            "tool_loop_limit": tool_loop_limit,
        }
        save_transcript(current_session_path, state)

    if args.resume:
        target_file = args.resume.strip() if isinstance(args.resume, str) else "interactive"
        chosen_transcript = None
        if target_file == "interactive":
            if sys.stdout.isatty():
                chosen_transcript = pick_transcript_interactive()
            else:
                recent = list_recent_transcripts()
                if recent:
                    chosen_transcript = recent[0]
        else:
            cand = resolve_path(target_file, Path.cwd())
            if not cand.exists() and TRANSCRIPTS_DIR.exists():
                cand = TRANSCRIPTS_DIR / target_file
            if cand.exists():
                try:
                    data = load_transcript(cand)
                    chosen_transcript = {"path": cand, "data": data}
                except Exception as exc:
                    error(f"Error loading transcript '{target_file}': {exc}")
            else:
                error(f"Transcript file not found: {target_file}")

        if chosen_transcript:
            t_data = chosen_transcript["data"]
            t_path = chosen_transcript["path"]
            system_instruction = t_data.get("system_instruction", system_instruction)
            client.model = t_data.get("model", client.model)
            p_root = t_data.get("project_root")
            if p_root:
                new_cwd = resolve_path(p_root, Path.cwd())
                if new_cwd.exists() and new_cwd.is_dir():
                    try:
                        os.chdir(new_cwd)
                        cwd = new_cwd
                        info(f"Changed working directory to: {cwd}")
                    except Exception as exc:
                        warn(f"Could not cd to project root '{new_cwd}': {exc}")
            contents = list(t_data.get("contents", []))
            tool_loop_limit = int(t_data.get("tool_loop_limit", tool_loop_limit) or tool_loop_limit)
            loaded_disabled_tools = t_data.get("disabled_tools")
            if isinstance(loaded_disabled_tools, list):
                disabled_tools = set(str(item) for item in loaded_disabled_tools)
            current_session_path = t_path
            info(f"Resumed session from {t_path.name} ({len(contents)} messages).")

    if args.load_transcript:
        transcript_path = resolve_path(args.load_transcript, Path.cwd())
        loaded = load_transcript(transcript_path)
        system_instruction = loaded.get("system_instruction", system_instruction)
        client.model = loaded.get("model", client.model)
        cwd = resolve_path(loaded.get("project_root", str(cwd)), Path.cwd())
        contents = list(loaded.get("contents", []))
        tool_loop_limit = int(loaded.get("tool_loop_limit", tool_loop_limit) or tool_loop_limit)
        loaded_disabled_tools = loaded.get("disabled_tools")
        if isinstance(loaded_disabled_tools, list):
            disabled_tools = set(str(item) for item in loaded_disabled_tools)
        elif "tools_enabled" in loaded and not bool(loaded.get("tools_enabled")):
            disabled_tools = set(all_tool_names)
        current_session_path = transcript_path

    title("Gemini Terminal CLI")
    info(f"Project root: {cwd}")
    info(failover_status_line())

    model_cache: List[Dict[str, Any]] = []

    def refresh_model_cache() -> List[Dict[str, Any]]:
        nonlocal model_cache
        try:
            model_cache = list_chat_models(client)
        except Exception as exc:
            warn(f"Could not load model list: {exc}")
            model_cache = []
        return model_cache

    def print_model_list(show_all: bool = False) -> None:
        models = refresh_model_cache()
        if not models:
            warn("No chat models found.")
            return
        shown_models = apply_cooldown_state(apply_model_tags(
            filter_models_for_display(models, hidden_models, show_all=show_all),
            speed_tags,
            model_usage_counts,
        ))
        print()
        title("Available Models")
        current_uses = int(model_usage_counts.get(client.model, 0) or 0)
        if show_all:
            print(f"Showing full catalog: {len(shown_models)} models. Current model: {client.model} [uses: {current_uses}]")
        else:
            print(f"Showing recommended models: {len(shown_models)} models. Current model: {client.model} [uses: {current_uses}]")
        print()
        widths = build_model_table_widths(shown_models)
        for line in build_model_table_header(widths):
            print(line)
        if show_all:
            index = 1
            for group in ("Stable", "Aliases", "Preview", "Gemma", "Image"):
                grouped_models = [m for m in shown_models if model_group(m) == group]
                if not grouped_models:
                    continue
                print(f"[{group}]")
                for model in grouped_models:
                    print(format_model_entry(index, model, client.model, widths=widths))
                    index += 1
                print()
        else:
            for index, model in enumerate(shown_models[:DEFAULT_MODEL_LIST_LIMIT], start=1):
                print(format_model_entry(index, model, client.model, widths=widths))
            if len(shown_models) > DEFAULT_MODEL_LIST_LIMIT:
                print()
                print("Tip: use /models all for the full catalog.")
        print()

    def get_recommended_models() -> List[Dict[str, Any]]:
        models = model_cache or refresh_model_cache()
        return apply_model_tags(
            filter_models_for_display(models, hidden_models, show_all=False),
            speed_tags,
            model_usage_counts,
        )

    def prune_model_cooldowns() -> None:
        expired = [name for name, until in model_cooldowns.items() if until <= _now()]
        for name in expired:
            model_cooldowns.pop(name, None)
            write_notification()

    def apply_cooldown_state(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prune_model_cooldowns()
        decorated: List[Dict[str, Any]] = []
        for model in models:
            copy_model = dict(model)
            name = model_name(model)
            cooldown_text = format_cooldown_until(model_cooldowns.get(name))
            if cooldown_text:
                copy_model["_state"] = cooldown_text
            elif copy_model.get("_hidden"):
                copy_model["_state"] = "hidden"
            else:
                copy_model["_state"] = ""
            decorated.append(copy_model)
        return decorated

    def get_token_estimate() -> int:
        total_chars = len(system_instruction) if system_instruction else 0
        for msg in contents:
            for part in msg.get("parts", []):
                if "text" in part:
                    total_chars += len(str(part["text"]))
                elif "functionCall" in part:
                    total_chars += len(json.dumps(part["functionCall"]))
                elif "functionResponse" in part:
                    total_chars += len(json.dumps(part["functionResponse"]))
        return total_chars // 4

    def prompt_text() -> str:
        prune_model_cooldowns()
        acc = active_api_account if active_api_account else "api"
        prefix = f"{acc} -> {client.model}"
        cooldown_text = format_cooldown_until(model_cooldowns.get(client.model))
        if cooldown_text:
            prefix += f" [{cooldown_text}]"
        
        tok_count = last_turn_tokens if last_turn_tokens is not None else (get_token_estimate() if contents else 0)
        if tok_count > 0:
            prefix += f" [{_format_token_count(tok_count)}]"

        return _ansi_wrap(f"{prefix}> ", prompt_prefix_color)

    def persist_selection() -> None:
        account_name = active_api_account or saved_last_api_account
        if account_name:
            api_account_model_prefs[account_name] = {"failover_uses": max(0, int(failover_uses))}
        save_model_prefs(
            hidden_models,
            speed_tags,
            model_usage_counts,
            failover_uses,
            sorted(disabled_tools),
            aliases,
            client.model,
            account_name,
            system_instruction,
            tool_loop_limit,
            auto_failover_default,
            auto_failover_projects,
            api_account_model_prefs,
            prompt_fg,
            prompt_bg,
            prompt_prefix_color,
        )

    def add_api_account_interactive(provider: str = "gemini") -> None:
        nonlocal api_accounts, tavily_accounts, api_accounts_loaded, model_cache
        provider = provider.lower().strip() or "gemini"
        label = "Tavily" if provider == "tavily" else "Gemini"
        name = input(f"{label} API name: ").strip()
        if not name:
            warn("API name is required.")
            return
        key = input(f"{label} API key: ").strip()
        if not key:
            warn("API key is required.")
            return
        accounts = ensure_api_accounts_loaded()
        api_accounts = accounts
        if provider == "tavily":
            tavily_accounts[name] = key
            print(save_api_accounts(api_accounts, password=args.api_password, tavily_accounts=tavily_accounts))
            api_accounts_loaded = True
            info(f"Saved Tavily API account: {name}")
            return
        api_accounts[name] = key
        switch_api_account(name, key)
        client.api_key = api_key
        model_cache = []
        print(save_api_accounts(api_accounts, password=args.api_password, tavily_accounts=tavily_accounts))
        api_accounts_loaded = True
        persist_selection()
        info(f"Loaded Gemini API account: {name}")

    def load_api_account_by_name(chosen_name: str) -> None:
        nonlocal model_cache
        accounts = ensure_api_accounts_loaded()
        if not accounts:
            warn("No saved API accounts. Use /api to add one.")
            return
        if not chosen_name or chosen_name not in accounts:
            warn("Unknown API account name.")
            return
        switch_api_account(chosen_name, accounts[chosen_name])
        client.api_key = api_key
        model_cache = []
        persist_selection()
        info(f"Loaded Gemini API account: {chosen_name}")

    def record_model_usage(model_name_value: str, amount: int = 1) -> None:
        if not model_name_value or amount <= 0:
            return
        model_usage_counts[model_name_value] = int(model_usage_counts.get(model_name_value, 0) or 0) + amount
        persist_selection()

    def retryable_account_error(message: str) -> bool:
        lowered = message.lower()
        return any(
            token in lowered
            for token in (
                "quota",
                "429",
                "rate limit",
                "too many requests",
                "resource exhausted",
                "resource has been exhausted",
                "limit exceeded",
                "exceeded your current quota",
                "high demand",
            )
        )

    def attempt_account_failover(failed_accounts: Set[str]) -> bool:
        nonlocal model_cache, failover_uses
        if not effective_auto_failover_enabled():
            return False
        accounts = ensure_api_accounts_loaded()
        if len(accounts) < 2:
            return False
        ordered_names = sorted(accounts.keys(), key=str.lower)
        current_name = active_api_account
        if current_name and current_name in ordered_names:
            start_index = ordered_names.index(current_name) + 1
            candidates = ordered_names[start_index:] + ordered_names[:start_index]
        else:
            candidates = ordered_names
        for candidate in candidates:
            if candidate == current_name or candidate in failed_accounts:
                continue
            switch_api_account(candidate, accounts[candidate])
            client.api_key = api_key
            failover_uses += 1
            model_cache = []
            persist_selection()
            info(f"Auto failover switched to API account: {candidate}")
            return True
        return False

    def run_turn(user_text: str) -> None:
        nonlocal contents
        contents.append(make_user_content_from_input(user_text, cwd))
        failed_accounts: Set[str] = set()

        try:
            for _ in range(tool_loop_limit):
                eff_system = get_effective_system_instruction(system_instruction, disabled_tools)
                try:
                    response = client.generate(
                        contents=contents,
                        system_instruction=eff_system,
                        tool_names=enabled_tool_names(disabled_tools),
                        temperature=args.temperature,
                        max_output_tokens=args.max_output_tokens,
                    )
                    record_model_usage(client.model)
                    usage = response.get("usageMetadata", {})
                    if isinstance(usage, dict) and "totalTokenCount" in usage:
                        nonlocal last_turn_tokens
                        last_turn_tokens = int(usage["totalTokenCount"])
                except RuntimeError as exc:
                    msg = str(exc).strip()
                    error(msg)
                    retry_match = re.search(r"Please retry in ([0-9]+(?:\.[0-9]+)?)s", msg, re.IGNORECASE)
                    if retry_match:
                        model_cooldowns[client.model] = _now() + dt.timedelta(minutes=1)
                        warn(f"Cooldown set for {client.model}: {format_cooldown_until(model_cooldowns.get(client.model))}")
                    if active_api_account:
                        failed_accounts.add(active_api_account)
                    if retryable_account_error(msg) and attempt_account_failover(failed_accounts):
                        warn(f"Retrying the same request with {active_api_account}.")
                        continue
                    if retryable_account_error(msg):
                        warn("Try /models and choose a more common chat model like 3.6 flash or 2.5 flash.")
                    return
                candidates = response.get("candidates", [])
                if not candidates:
                    error("Gemini returned no candidates.")
                    return

                content_obj = candidates[0].get("content", {})
                parts = content_obj.get("parts", [])
                text = render_model_parts(parts)
                if text:
                    nonlocal last_assistant_response_text
                    last_assistant_response_text = text
                    print()
                    print(text)
                    print()

                function_calls = extract_function_calls(parts)
                if not function_calls:
                    contents.append(content_obj)
                    return

                contents.append(content_obj)
                responses: List[Dict[str, Any]] = []
                for function_call in function_calls:
                    name = function_call.get("name", "")
                    call_args = function_call.get("args", {}) or {}
                    info(format_tool_call(name, call_args))
                    result = execute_tool(name, call_args, cwd, ensure_tavily_accounts_loaded())
                    responses.append(
                        {
                            "functionResponse": {
                                "name": name,
                                "response": {"result": result},
                            }
                        }
                    )
                    formatted_res = format_tool_result(result)
                    if result.lower().startswith("error") or "error:" in result.lower():
                        error(formatted_res)
                    else:
                        info(formatted_res)

                contents.append({"role": "user", "parts": responses})

            warn(f"Reached the maximum tool-call loop depth ({tool_loop_limit}).")
        except KeyboardInterrupt:
            print()
            warn("Interrupted by user.")
        finally:
            auto_save_session()
            write_notification()

    if args.prompt:
        run_turn(args.prompt)
    else:
        command_history: List[str] = load_prompt_history()
        while True:
            try:
                user_input = read_dynamic_prompt(
                    prompt_text,
                    command_history,
                    cwd=cwd,
                    prompt_fg=prompt_fg,
                    prompt_bg=prompt_bg,
                ).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not user_input:
                user_input = "continue"
                info("continue")
            append_prompt_history(user_input, command_history)
            if user_input.startswith("/"):
                command, _, remainder = user_input.partition(" ")
                command = command.lower()
                remainder = remainder.strip()

                if command in {"/exit", "/quit"}:
                    break
                if command == "/help":
                    print_help()
                    continue
                if command in {"/setting", "/settings"}:
                    presets = [
                        {"name": "Classic Red", "fg": "ansired", "bg": ""},
                        {"name": "Matrix Green", "fg": "ansibrightgreen", "bg": ""},
                        {"name": "Cyber Cyan", "fg": "ansibrightcyan", "bg": ""},
                        {"name": "Solar Yellow", "fg": "ansibrightyellow", "bg": ""},
                        {"name": "Royal Purple", "fg": "ansimagenta", "bg": ""},
                        {"name": "Ocean Bar", "fg": "#ffffff", "bg": "#005f87"},
                        {"name": "Fire Bar", "fg": "#ffffff", "bg": "#870000"},
                        {"name": "Neon Dark Bar", "fg": "#00ffaf", "bg": "#262626"},
                    ]
                    fg_colors = [
                        {"name": "Red", "value": "ansired"},
                        {"name": "Bright Red", "value": "ansibrightred"},
                        {"name": "Green", "value": "ansigreen"},
                        {"name": "Bright Green", "value": "ansibrightgreen"},
                        {"name": "Cyan", "value": "ansibrightcyan"},
                        {"name": "Yellow", "value": "ansibrightyellow"},
                        {"name": "Magenta", "value": "ansimagenta"},
                        {"name": "White", "value": "ansiwhite"},
                        {"name": "Custom Hex / Name", "value": "custom"},
                    ]
                    bg_colors = [
                        {"name": "None (Transparent)", "value": ""},
                        {"name": "Dark Gray Bar", "value": "#262626"},
                        {"name": "Navy Blue Bar", "value": "#005f87"},
                        {"name": "Dark Red Bar", "value": "#5f0000"},
                        {"name": "Dark Green Bar", "value": "#005f00"},
                        {"name": "Dark Purple Bar", "value": "#3a005f"},
                        {"name": "Custom Hex / Name", "value": "custom"},
                    ]
                    while True:
                        s_items = [
                            {"key": "preset", "title": "Preset Color Themes", "desc": "1-click ready-made themes"},
                            {"key": "fg", "title": "Prompt Foreground Color (FG)", "desc": f"Current: {prompt_fg}"},
                            {"key": "bg", "title": "Prompt Background Color (BG)", "desc": f"Current: {prompt_bg or 'none'}"},
                            {"key": "loops", "title": "Tool Loop Limit", "desc": f"Current: {tool_loop_limit}"},
                            {"key": "failover", "title": "Auto Failover Settings", "desc": f"Current: {format_auto_failover_status()}"},
                        ]
                        def render_settings_item(item: Dict[str, Any], idx: int, sel: bool = False) -> str:
                            marker = ">" if sel else " "
                            row = f"{marker} {idx + 1:>2}. {item['title']:<32}  {item['desc']}"
                            if sel:
                                return _ansi_wrap(row, "48;5;24;97")
                            return row

                        c_setting = interactive_select(
                            title_text="",
                            items=s_items,
                            render_item=render_settings_item,
                            header_lines=None,
                            dynamic_footer=None,
                            footer_lines=["  Use Up/Down to navigate, Enter to select, Esc/Q to exit."],
                            instructions="",
                        )
                        if not c_setting:
                            break
                        sk = c_setting["key"]
                        if sk == "preset":
                            def render_preset(p_item: Dict[str, Any], idx: int, sel: bool = False) -> str:
                                marker = ">" if sel else " "
                                bg_d = f"bg:{p_item['bg']}" if p_item['bg'] else "transparent"
                                row = f"{marker} {idx + 1:>2}. {p_item['name']:<20}  (FG: {p_item['fg']}, BG: {bg_d})"
                                if sel:
                                    return _ansi_wrap(row, "48;5;24;97")
                                return row
                            c_p = interactive_select(
                                title_text="",
                                items=presets,
                                render_item=render_preset,
                                header_lines=None,
                                footer_lines=["  Press Enter to apply preset theme, Esc to cancel."],
                                instructions="",
                            )
                            if c_p:
                                prompt_fg = c_p["fg"]
                                prompt_bg = c_p["bg"]
                                persist_selection()
                                info(f"Applied theme '{c_p['name']}' (FG: {prompt_fg}, BG: {prompt_bg or 'none'})")
                        elif sk == "fg":
                            def render_fg(f_item: Dict[str, Any], idx: int, sel: bool = False) -> str:
                                marker = ">" if sel else " "
                                row = f"{marker} {idx + 1:>2}. {f_item['name']:<20}  ({f_item['value']})"
                                if sel:
                                    return _ansi_wrap(row, "48;5;24;97")
                                return row
                            c_f = interactive_select(
                                title_text="",
                                items=fg_colors,
                                render_item=render_fg,
                                header_lines=None,
                                footer_lines=["  Press Enter to select color, Esc to cancel."],
                                instructions="",
                            )
                            if c_f:
                                if c_f["value"] == "custom":
                                    val = input("Enter custom color (e.g. #ff0055, ansigreen, ansicyan): ").strip()
                                    if val:
                                        prompt_fg = val
                                        persist_selection()
                                        info(f"Set prompt text color to '{val}'")
                                else:
                                    prompt_fg = c_f["value"]
                                    persist_selection()
                                    info(f"Set prompt text color to '{prompt_fg}'")
                        elif sk == "bg":
                            def render_bg(b_item: Dict[str, Any], idx: int, sel: bool = False) -> str:
                                marker = ">" if sel else " "
                                val_s = b_item['value'] or "none"
                                row = f"{marker} {idx + 1:>2}. {b_item['name']:<22}  ({val_s})"
                                if sel:
                                    return _ansi_wrap(row, "48;5;24;97")
                                return row
                            c_b = interactive_select(
                                title_text="",
                                items=bg_colors,
                                render_item=render_bg,
                                header_lines=None,
                                footer_lines=["  Press Enter to select background color, Esc to cancel."],
                                instructions="",
                            )
                            if c_b:
                                if c_b["value"] == "custom":
                                    val = input("Enter custom background (e.g. #262626, ansiblue): ").strip()
                                    prompt_bg = val
                                    persist_selection()
                                    info(f"Set prompt background color to '{val or 'none'}'")
                                else:
                                    prompt_bg = c_b["value"]
                                    persist_selection()
                                    info(f"Set prompt background color to '{prompt_bg or 'none'}'")
                        elif sk == "loops":
                            val = input(f"Enter tool loop limit (current: {tool_loop_limit}): ").strip()
                            if val:
                                try:
                                    n = int(val)
                                    if n > 0:
                                        tool_loop_limit = n
                                        persist_selection()
                                        info(f"Tool loop limit updated to {tool_loop_limit}")
                                except ValueError:
                                    warn("Invalid number.")
                        elif sk == "failover":
                            f_items = [
                                {
                                    "key": "global",
                                    "title": "Global Default (All New Projects)",
                                    "desc": f"Current: {'ON' if auto_failover_default else 'OFF'} (Applies to all new projects)",
                                },
                                {
                                    "key": "project",
                                    "title": "Current Project Setting",
                                    "desc": f"Current: {'INHERIT' if current_project_auto_failover_state() is None else ('ON' if current_project_auto_failover_state() else 'OFF')}",
                                },
                                {
                                    "key": "picker",
                                    "title": "Full Failover Scope Manager",
                                    "desc": "Manage Project, Session, and Global scopes together",
                                },
                            ]
                            c_f = interactive_select(
                                title_text="",
                                items=f_items,
                                render_item=render_settings_item,
                                header_lines=None,
                                dynamic_footer=None,
                                footer_lines=["  Use Up/Down to navigate, Enter to select, Esc to return."],
                                instructions="",
                            )
                            if c_f:
                                if c_f["key"] == "global":
                                    auto_failover_default = not auto_failover_default
                                    persist_selection()
                                    info(f"Global failover default set to {'ON' if auto_failover_default else 'OFF'} for all new projects.")
                                elif c_f["key"] == "project":
                                    curr = current_project_auto_failover_state()
                                    if curr is None:
                                        set_project_auto_failover(True)
                                    elif curr is True:
                                        set_project_auto_failover(False)
                                    else:
                                        clear_project_auto_failover()
                                    info(failover_status_line())
                                elif c_f["key"] == "picker":
                                    chosen_f = pick_failover_interactive(
                                        current_project_auto_failover_state(),
                                        auto_failover_session_override,
                                        auto_failover_default,
                                    )
                                    if chosen_f is not None:
                                        apply_failover_picker_state(chosen_f)
                                        info(failover_status_line())
                    continue
                if command == "/reset":
                    contents = []
                    last_turn_tokens = None
                    info("Conversation cleared.")
                    continue
                if command in {"/mm", "/test"}:
                    if not model_cache:
                        refresh_model_cache()
                    if command == "/test" or remainder.lower() in {"test", "test all"}:
                        failed_models = test_all_models(client, model_cache)
                        speed_tags.update(getattr(test_all_models, "last_speed_tags", {}))
                        passed_models = list(getattr(test_all_models, "last_passed_models", []))
                        for model_name_value in passed_models:
                            model_usage_counts[model_name_value] = int(model_usage_counts.get(model_name_value, 0) or 0) + 1
                        passed_set = set(passed_models)
                        unhidden_count = sum(1 for m in hidden_models if m in passed_set)
                        if unhidden_count:
                            hidden_models = [m for m in hidden_models if m not in passed_set]
                        hidden_set = set(hidden_models)
                        new_hidden = [m for m in failed_models if m not in hidden_set]
                        if new_hidden:
                            hidden_models.extend(new_hidden)
                        persist_selection()
                        if unhidden_count:
                            info(f"Restored {unhidden_count} passing model(s).")
                        if new_hidden:
                            info(f"Auto-hidden {len(new_hidden)} failed model(s).")
                        continue
                    if remainder:
                        chosen = choose_model_from_list(model_cache, remainder)
                        if chosen:
                            client.model = chosen
                            info(f"Model set to {client.model}")
                            persist_selection()
                        else:
                            warn("Unknown model selection. Use /mm to pick from the list or /test.")
                    else:
                        visible_models = apply_cooldown_state(apply_model_tags(
                            [
                                m for m in filter_models_for_display(model_cache, hidden_models, show_all=True)
                                if not m.get("_hidden")
                            ],
                            speed_tags,
                            model_usage_counts,
                        ))
                        chosen = pick_model_interactive(
                            visible_models,
                            client.model,
                            title_text="Select Model",
                            model_cooldowns=model_cooldowns,
                        )
                        if chosen:
                            client.model = chosen
                            info(f"Model set to {client.model}")
                            persist_selection()
                    continue
                if command == "/api":
                    accounts = ensure_api_accounts_loaded()
                    if remainder:
                        load_api_account_by_name(remainder)
                        continue
                    chosen_api = pick_api_account_interactive(
                        accounts,
                        ensure_tavily_accounts_loaded(),
                        active_api_account,
                        api_account_model_prefs,
                    )
                    if not chosen_api:
                        continue
                    if chosen_api["action"] == "add":
                        add_api_account_interactive(chosen_api["provider"])
                    elif chosen_api["provider"] == "tavily":
                        info(f"Tavily API account saved: {chosen_api['name']}")
                    else:
                        load_api_account_by_name(chosen_api["name"])
                    continue
                if command == "/loops":
                    if not remainder:
                        info(f"Current tool loop limit: {tool_loop_limit}")
                    else:
                        try:
                            new_limit = int(remainder)
                            if new_limit < 1:
                                raise ValueError
                        except ValueError:
                            warn("Usage: /loops <positive number>")
                            continue
                        tool_loop_limit = new_limit
                        persist_selection()
                        info(f"Tool loop limit set to {tool_loop_limit}")
                    continue
                if command == "/failover":
                    parts = remainder.lower().split()
                    if not parts:
                        chosen = pick_failover_interactive(
                            current_project_auto_failover_state(),
                            auto_failover_session_override,
                            auto_failover_default,
                        )
                        if chosen is None:
                            continue
                        apply_failover_picker_state(chosen)
                        info(failover_status_line())
                        continue
                    if len(parts) == 1 and parts[0] in {"status", "show"}:
                        info(failover_status_line())
                        info(f"Global default: {'on' if auto_failover_default else 'off'}")
                        project_setting = current_project_auto_failover_state()
                        info(
                            "Project override: "
                            + ("none" if project_setting is None else ("on" if project_setting else "off"))
                        )
                        info(
                            "Session override: "
                            + (
                                "none"
                                if auto_failover_session_override is None
                                else ("on" if auto_failover_session_override else "off")
                            )
                        )
                        continue
                    if len(parts) == 1 and parts[0] in {"on", "off"}:
                        set_project_auto_failover(parts[0] == "on")
                        info(f"Auto failover set to {'on' if effective_auto_failover_enabled() else 'off'} for this project.")
                        continue
                    if len(parts) == 1 and parts[0] in {"clear", "reset"}:
                        clear_project_auto_failover()
                        info(f"Auto failover reset to {'on' if effective_auto_failover_enabled() else 'off'} from the global default.")
                        continue
                    if len(parts) == 2 and parts[0] == "session" and parts[1] in {"on", "off"}:
                        set_session_auto_failover(parts[1] == "on")
                        info(f"Auto failover session override set to {'on' if effective_auto_failover_enabled() else 'off'}.")
                        continue
                    if len(parts) == 2 and parts[0] in {"default", "global"} and parts[1] in {"on", "off"}:
                        auto_failover_default = parts[1] == "on"
                        set_session_auto_failover(None)
                        persist_selection()
                        info(f"Auto failover global default set to {'on' if auto_failover_default else 'off'}.")
                        continue
                    warn("Usage: /failover [status|on|off|clear|reset|session on|session off|default on|default off]")
                    continue
                if command == "/tool":
                    changed = pick_tool_interactive(disabled_tools)
                    if changed:
                        persist_selection()
                        info(f"Tool settings updated. Enabled: {len(enabled_tool_names(disabled_tools))}/{len(all_tool_names)}")
                    continue
                if command == "/system":
                    if remainder:
                        content, found = resolve_system_instruction_input(remainder, cwd)
                        if not found:
                            warn(f"Warning: File not found or path invalid: {remainder}")
                            warn("The system instruction has been set to that literal text instead.")
                        
                        system_instruction = content
                        persist_selection()
                        
                        if found:
                            info(f"System instruction loaded from file.")
                        else:
                            info("System instruction updated with provided text.")
                    else:
                        info("Current System Instruction:")
                        print(_ansi_wrap("-" * 40, "90"))
                        print(system_instruction)
                        print(_ansi_wrap("-" * 40, "90"))
                        print("Usage: /system <text|file> to update.")
                    continue
                if command == "/skill":
                    skills = list_skills(cwd=cwd)
                    if not skills:
                        warn("No skills found in 'skills/' directory.")
                        continue
                    if remainder:
                        matched_path = None
                        for _, _, path in skills:
                            if path.stem.lower() == remainder.lower() or path.name.lower() == remainder.lower():
                                matched_path = path
                                break
                        if not matched_path:
                            for _, _, path in skills:
                                if remainder.lower() in path.stem.lower():
                                    matched_path = path
                                    break
                        if matched_path:
                            try:
                                skill_content = matched_path.read_text(encoding="utf-8", errors="replace")
                                contents.append(make_user_content(f"Skill instructions loaded:\n\n{skill_content}"))
                                info(f"Skill instructions loaded from {matched_path.name}.")
                            except Exception as exc:
                                error(f"Error reading skill: {exc}")
                        else:
                            warn(f"Skill not found: {remainder}. Available skills: {', '.join(p.stem for _, _, p in skills)}")
                    else:
                        chosen_skill = pick_skill_interactive(cwd=cwd)
                        if chosen_skill:
                            contents.append(make_user_content(f"Skill instructions loaded:\n\n{chosen_skill}"))
                            info("Skill instructions loaded.")
                    continue
                if command in {"/resume", "/r"}:
                    chosen_transcript = None
                    if remainder:
                        cand = resolve_path(remainder, Path.cwd())
                        if not cand.exists() and TRANSCRIPTS_DIR.exists():
                            cand = TRANSCRIPTS_DIR / remainder
                        if cand.exists():
                            try:
                                data = load_transcript(cand)
                                chosen_transcript = {"path": cand, "data": data}
                            except Exception as exc:
                                error(f"Error loading transcript '{remainder}': {exc}")
                        else:
                            warn(f"Transcript file not found: {remainder}")
                    else:
                        chosen_transcript = pick_transcript_interactive(client=client)

                    if chosen_transcript:
                        t_data = chosen_transcript["data"]
                        t_path = chosen_transcript["path"]
                        system_instruction = t_data.get("system_instruction", system_instruction)
                        client.model = t_data.get("model", client.model)
                        p_root = t_data.get("project_root")
                        if p_root:
                            new_cwd = resolve_path(p_root, Path.cwd())
                            if new_cwd.exists() and new_cwd.is_dir():
                                try:
                                    os.chdir(new_cwd)
                                    cwd = new_cwd
                                    info(f"Changed working directory to: {cwd}")
                                except Exception as exc:
                                    warn(f"Could not cd to project root '{new_cwd}': {exc}")
                        contents = list(t_data.get("contents", []))
                        tool_loop_limit = int(t_data.get("tool_loop_limit", tool_loop_limit) or tool_loop_limit)
                        loaded_disabled_tools = t_data.get("disabled_tools")
                        if isinstance(loaded_disabled_tools, list):
                            disabled_tools = set(str(item) for item in loaded_disabled_tools)
                        current_session_path = t_path
                        last_turn_tokens = None
                        info(f"Resumed session from {t_path.name} ({len(contents)} messages).")
                    continue
                if command == "/tokens":
                    # Calculate total character count including text, function calls, responses, and system instruction
                    eff_sys = get_effective_system_instruction(system_instruction, disabled_tools)
                    total_chars = len(eff_sys) if eff_sys else 0
                    for msg in contents:
                        for part in msg.get("parts", []):
                            if "text" in part:
                                total_chars += len(str(part["text"]))
                            elif "functionCall" in part:
                                total_chars += len(json.dumps(part["functionCall"]))
                            elif "functionResponse" in part:
                                total_chars += len(json.dumps(part["functionResponse"]))

                    actual_tokens = None
                    if contents and api_key:
                        try:
                            actual_tokens = client.count_tokens(contents, system_instruction=eff_sys)
                        except Exception:
                            actual_tokens = None

                    est_tokens = total_chars // 4
                    if actual_tokens is not None and actual_tokens > 0:
                        info(f"Conversation tokens ({client.model}): {actual_tokens:,} tokens ({total_chars:,} chars across {len(contents)} messages)")
                    else:
                        info(f"Estimated conversation tokens (~4 chars/token): ~{est_tokens:,} tokens ({total_chars:,} chars across {len(contents)} messages)")
                    continue

                if command == "/run":
                    if not last_assistant_response_text:
                        warn("No recent assistant response with code blocks found.")
                        continue
                    # Extract code blocks from markdown text
                    code_block_pattern = re.compile(r"```(?:\w+)?\s*\n(.*?)```", re.DOTALL)
                    blocks = code_block_pattern.findall(last_assistant_response_text)
                    if not blocks:
                        warn("No code blocks found in the last assistant response.")
                        continue
                    
                    for idx, block in enumerate(blocks, start=1):
                        code = block.strip()
                        info(f"--- Executing Code Block {idx} ---")
                        print(_ansi_wrap(code, "90"))
                        res = run_powershell_command(code, cwd)
                        print(res)
                        info("------------------------------------")
                    continue

                if command == "/alias":
                    parts = remainder.split(maxsplit=1)
                    sub = parts[0].lower() if parts else "list"
                    arg = parts[1].strip() if len(parts) > 1 else ""

                    if sub == "list":
                        if not aliases:
                            info("No custom aliases saved. Use /alias add <name> <prompt>.")
                        else:
                            info("Saved Aliases:")
                            for name, prompt in sorted(aliases.items()):
                                print(f"  {name} -> {prompt}")
                        continue
                    elif sub == "add":
                        name_prompt = arg.split(maxsplit=1)
                        if len(name_prompt) < 2:
                            warn("Usage: /alias add <name> <prompt text>")
                            continue
                        a_name, a_text = name_prompt[0], name_prompt[1]
                        aliases[a_name] = a_text
                        persist_selection()
                        info(f"Added alias '{a_name}' -> {a_text}")
                        continue
                    elif sub == "remove" or sub == "rm":
                        if not arg:
                            warn("Usage: /alias remove <name>")
                            continue
                        if arg in aliases:
                            aliases.pop(arg)
                            persist_selection()
                            info(f"Removed alias '{arg}'")
                        else:
                            warn(f"Alias not found: {arg}")
                        continue
                    else:
                        warn("Usage: /alias [list|add <name> <prompt>|remove <name>]")
                        continue


                if command == "/save":
                    if remainder:
                        transcript_path = resolve_path(remainder, Path.cwd())
                        state = {
                            "model": client.model,
                            "system_instruction": system_instruction,
                            "project_root": str(cwd),
                            "disabled_tools": sorted(disabled_tools),
                            "contents": contents,
                            "tool_loop_limit": tool_loop_limit,
                        }
                        print(save_transcript(transcript_path, state))
                    else:
                        warn("Usage: /save <file>")
                    continue
                if command == "/load":
                    if remainder:
                        transcript_path = resolve_path(remainder, Path.cwd())
                        loaded = load_transcript(transcript_path)
                        client.model = loaded.get("model", client.model)
                        system_instruction = loaded.get("system_instruction", system_instruction)
                        cwd = resolve_path(loaded.get("project_root", str(cwd)), Path.cwd())
                        loaded_disabled_tools = loaded.get("disabled_tools")
                        if isinstance(loaded_disabled_tools, list):
                            disabled_tools = set(str(item) for item in loaded_disabled_tools)
                        elif "tools_enabled" in loaded and not bool(loaded.get("tools_enabled")):
                            disabled_tools = set(all_tool_names)
                        contents = list(loaded.get("contents", []))
                        info(f"Loaded transcript from {transcript_path}")
                    else:
                        warn("Usage: /load <file>")
                    continue

                warn(f"Unknown command: {command}")
                continue

            run_turn(user_input)

    if args.save_transcript:
        transcript_path = resolve_path(args.save_transcript, Path.cwd())
        state = {
            "model": client.model,
            "system_instruction": system_instruction,
            "project_root": str(cwd),
            "disabled_tools": sorted(disabled_tools),
            "contents": contents,
            "tool_loop_limit": tool_loop_limit,
        }
        print(save_transcript(transcript_path, state))

    auto_save_session()
    persist_selection()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
