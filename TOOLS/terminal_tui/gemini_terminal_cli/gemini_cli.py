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


DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_SYSTEM = (
    "You are a terminal coding assistant. "
    "Be concise, practical, and ask before making destructive changes. "
    "When editing code, prefer search_file and minimal block edits "
    "(replace_block, insert_after, delete_block) over rewriting whole files."
)
DEFAULT_TOOL_LOOPS = 8
MAX_TEXT_CHARS = 12000
DEFAULT_MODEL_LIST_LIMIT = 12
MODELS_PAGE_SIZE = 1000
MODEL_PREFS_FILE = Path(__file__).with_name("model_prefs.json")
API_ACCOUNTS_FILE = Path(__file__).with_name("api_accounts.lock")
API_ACCOUNTS_LEGACY_FILE = Path(__file__).with_name("api_accounts.json")
API_ACCOUNTS_MAGIC = b"GEMAPI1"
NOTIFICATION_FILE = Path(r"C:\Users\nahid\notification.txt")

try:
    import msvcrt
except Exception:
    msvcrt = None


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


def _format_seconds(seconds: float) -> str:
    total = max(0, int(seconds + 0.999))
    minutes, secs = divmod(total, 60)
    return f"{minutes:02d}:{secs:02d}"


def info(text: str) -> None:
    print(_ansi_wrap(text, "36"))


def warn(text: str) -> None:
    print(_ansi_wrap(text, "33"))


def error(text: str) -> None:
    print(_ansi_wrap(text, "31"))


def read_dynamic_prompt(prompt_provider: Callable[[], str], history: Optional[List[str]] = None) -> str:
    """Read a line while allowing a time-sensitive prompt to refresh."""
    if msvcrt is None or not sys.stdin.isatty() or not sys.stdout.isatty():
        return input(prompt_provider())

    buffer: List[str] = []
    displayed_prompt = ""
    next_refresh = 0.0
    history_index = len(history or [])

    def redraw(force: bool = False) -> None:
        nonlocal displayed_prompt, next_refresh
        now = time.monotonic()
        if not force and now < next_refresh:
            return
        prompt = prompt_provider()
        if force or prompt != displayed_prompt:
            sys.stdout.write("\r\033[2K" + prompt + "".join(buffer))
            sys.stdout.flush()
            displayed_prompt = prompt
        next_refresh = now + 0.25

    redraw(force=True)
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getwch()
            if char in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                return "".join(buffer)
            if char == "\003":
                raise KeyboardInterrupt
            if char in ("\x00", "\xe0"):
                char2 = msvcrt.getwch()
                if history and char2 == "H":
                    history_index = max(0, history_index - 1)
                    buffer = list(history[history_index])
                    redraw(force=True)
                elif history and char2 == "P":
                    history_index = min(len(history), history_index + 1)
                    buffer = list(history[history_index]) if history_index < len(history) else []
                    redraw(force=True)
                continue
            if char == "\x08":
                if buffer:
                    buffer.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            if char.isprintable():
                buffer.append(char)
                sys.stdout.write(char)
                sys.stdout.flush()
        else:
            redraw()
            time.sleep(0.05)


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
    "run_shell_command": {
        "name": "run_shell_command",
        "description": "Run a shell command.",
        "parameters": {
            "type": "OBJECT",
            "properties": {"command": {"type": "STRING"}},
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
    if name == "replace_block":
        filepath = resolve_path(args.get("filepath", ""), cwd)
        old_text = str(args.get("old_text", ""))
        new_text = str(args.get("new_text", ""))
        occurrence = int(args.get("occurrence", 1) or 1)
        return replace_block_in_file(filepath, old_text, new_text, occurrence=occurrence)
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
    if name == "run_shell_command":
        return run_shell_command(str(args.get("command", "")), cwd)
    if name == "request_follow_up":
        reason = args.get("reason") or "Continuing..."
        return f"Follow-up turn granted: {reason}"
    return f"Unknown tool: {name}"


def list_tool_catalog() -> List[Dict[str, str]]:
    return [
        {"name": "read_file", "description": "Read a local file."},
        {"name": "write_file", "description": "Write content to a local file."},
        {"name": "replace_file", "description": "Replace the full contents of a file."},
        {"name": "delete_file", "description": "Delete a local file or directory."},
        {"name": "list_directory", "description": "List directory contents."},
        {"name": "get_system_info", "description": "Get system information."},
        {"name": "search_file", "description": "Search text within a file or directory."},
        {"name": "search_web", "description": "Search the web without a saved API key."},
        {"name": "search_tavily", "description": "Search the web with saved Tavily API keys."},
        {"name": "replace_block", "description": "Replace an exact block of text in a file."},
        {"name": "insert_after", "description": "Insert text after an exact anchor in a file."},
        {"name": "delete_block", "description": "Delete an exact block of text from a file."},
        {"name": "run_shell_command", "description": "Run a shell command."},
        {"name": "request_follow_up", "description": "Request another turn for multi-step work."},
    ]


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
    return f"cooldown {_format_seconds(remaining)}"


class GeminiClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

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
    text = re.sub(r"(?<!\*)\*\*(.+?)\*\*(?!\*)", lambda m: _style_text(m.group(1), "1"), text)
    text = re.sub(r"(?<!_)__(.+?)__(?!_)", lambda m: _style_text(m.group(1), "1"), text)
    text = re.sub(r"(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)", lambda m: _style_text(m.group(1), "3"), text)
    text = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", lambda m: _style_text(m.group(1), "3"), text)
    text = re.sub(r"`([^`]+)`", lambda m: _style_text(m.group(1), "38;5;214"), text)
    return text


def render_markdown_text(text: str) -> str:
    lines: List[str] = []
    in_code_block = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        fence = re.match(r"^\s*```(\w+)?\s*$", line)
        if fence:
            in_code_block = not in_code_block
            language = fence.group(1) or ""
            fence_label = f"```{language}" if language else "```"
            lines.append(_style_text(fence_label, "90"))
            continue
        if in_code_block:
            lines.append(f"  {raw_line}")
            continue
        if not line.strip():
            lines.append("")
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            content = _render_inline_markdown(heading.group(2).strip())
            if level <= 2:
                lines.append(_style_text(content, "1;35"))
            elif level == 3:
                lines.append(_style_text(content, "1;36"))
            else:
                lines.append(_style_text(content, "1"))
            continue

        bullet = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if bullet:
            lines.append(f"• {_render_inline_markdown(bullet.group(1))}")
            continue

        ordered = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if ordered:
            lines.append(f"{ordered.group(1)}. {_render_inline_markdown(ordered.group(2))}")
            continue

        quote = re.match(r"^\s*>\s?(.*)$", line)
        if quote:
            lines.append(f"{_style_text('> ', '90')}{_render_inline_markdown(quote.group(1))}")
            continue

        horizontal_rule = re.match(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", line)
        if horizontal_rule:
            lines.append(_style_text("─" * 32, "90"))
            continue

        lines.append(_render_inline_markdown(line))

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


def format_tool_call(name: str, args: Dict[str, Any]) -> str:
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
    lines = ["[tool-result]"]
    if text:
        lines.extend(f"  {line}" for line in text.splitlines())
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
    return {
        "hidden_models": [str(item) for item in hidden],
        "speed_tags": {str(k): str(v) for k, v in speed_tags.items()},
        "model_usage_counts": {str(k): int(v) for k, v in usage_counts.items()},
    }


def default_model_prefs() -> Dict[str, Any]:
    return {
        **empty_account_model_prefs(),
        "api_accounts": {},
        "disabled_tools": [],
        "last_model": DEFAULT_MODEL,
        "last_api_account": "",
        "tool_loop_limit": DEFAULT_TOOL_LOOPS,
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
        disabled_tools = data.get("disabled_tools", [])
        if not isinstance(disabled_tools, list):
            disabled_tools = []
        prefs = dict(account_model_prefs)
        prefs.update({
            "api_accounts": normalized_api_accounts,
            "disabled_tools": [str(item) for item in disabled_tools],
            "last_model": str(data.get("last_model") or DEFAULT_MODEL),
            "last_api_account": last_api_account,
            "tool_loop_limit": int(data.get("tool_loop_limit") or DEFAULT_TOOL_LOOPS),
        })
        return prefs
    except Exception:
        return default_model_prefs()


def serialize_model_prefs(
    hidden_models: List[str],
    speed_tags: Dict[str, str],
    model_usage_counts: Dict[str, int],
) -> Dict[str, Any]:
    return {
        "hidden_models": sorted(set(hidden_models)),
        "speed_tags": dict(sorted(speed_tags.items())),
        "model_usage_counts": dict(sorted((str(k), int(v)) for k, v in model_usage_counts.items())),
    }


def save_model_prefs(
    hidden_models: List[str],
    speed_tags: Dict[str, str],
    model_usage_counts: Dict[str, int],
    disabled_tools: List[str],
    last_model: str,
    last_api_account: str,
    tool_loop_limit: int,
    api_account_model_prefs: Optional[Dict[str, Dict[str, Any]]] = None,
) -> str:
    account_model_prefs = serialize_model_prefs(hidden_models, speed_tags, model_usage_counts)
    api_accounts = {
        str(account_name): serialize_model_prefs(
            list(account_prefs.get("hidden_models", [])),
            dict(account_prefs.get("speed_tags", {})),
            dict(account_prefs.get("model_usage_counts", {})),
        )
        for account_name, account_prefs in (api_account_model_prefs or {}).items()
    }
    if last_api_account:
        api_accounts[last_api_account] = account_model_prefs
    payload = {
        **account_model_prefs,
        "api_accounts": dict(sorted(api_accounts.items())),
        "disabled_tools": sorted(set(disabled_tools)),
        "last_model": last_model,
        "last_api_account": last_api_account,
        "tool_loop_limit": int(tool_loop_limit),
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
        os.system("cls")


def read_key() -> str:
    if msvcrt is None:
        return input().strip()
    ch = msvcrt.getwch()
    if ch in ("\x00", "\xe0"):
        ch2 = msvcrt.getwch()
        return ch + ch2
    return ch


def interactive_select(
    title_text: str,
    items: List[Dict[str, Any]],
    render_item,
    header_lines: Optional[List[str]] = None,
    footer_lines: Optional[List[str]] = None,
    instructions: str = "Use Up/Down, Enter to choose, Esc to cancel.",
    on_space: Optional[Callable[[Dict[str, Any], int], None]] = None,
) -> Optional[Dict[str, Any]]:
    if not items:
        return None
    index = 0
    footer_lines = footer_lines or []

    while True:
        clear_screen()
        title(title_text)
        print(instructions)
        print()
        if header_lines:
            for line in header_lines:
                print(line)
            print()
        for i, item in enumerate(items):
            line = render_item(item, i, i == index)
            print(line)
        if footer_lines:
            print()
            for line in footer_lines:
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
        elif key == " " and on_space is not None:
            on_space(items[index], index)
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
        title_text=title_text,
        items=decorated_models,
        render_item=render_item,
        header_lines=build_model_table_header(widths),
        footer_lines=["Press Q or Esc to cancel."],
    )
    if not chosen:
        return None
    return model_name(chosen)


def build_tool_table_widths(tools: List[Dict[str, Any]]) -> Dict[str, int]:
    name_width = 0
    desc_width = 0
    for tool in tools:
        name_width = max(name_width, len(str(tool.get("name", ""))))
        desc_width = max(desc_width, len(str(tool.get("description", ""))))
    return {
        "name": min(max(name_width, 10), 26),
        "description": min(max(desc_width, 24), 56),
    }


def build_tool_table_header(widths: Dict[str, int]) -> List[str]:
    return [
        f"  {'Id':>2}  {'Tool':<{widths['name']}}  {'Description':<{widths['description']}}  State",
        f"  {'--':>2}  {'-' * widths['name']}  {'-' * widths['description']}  -----",
    ]


def format_tool_entry(
    index: int,
    tool: Dict[str, Any],
    widths: Dict[str, int],
    selected: bool = False,
) -> str:
    name = str(tool.get("name", ""))
    description = str(tool.get("description", ""))
    enabled = bool(tool.get("enabled", True))
    marker = ">" if selected else " "
    state = "on" if enabled else "off"
    state_text = _ansi_wrap(state, "31") if not enabled else _ansi_wrap(state, "32")
    row = (
        f"{marker} {index:>2}  "
        f"{name:<{widths['name']}}  "
        f"{description:<{widths['description']}}  "
        f"{state_text}"
    ).rstrip()
    if selected:
        return _ansi_wrap(row, "48;5;24;97")
    if not enabled:
        return _ansi_wrap(row, "31")
    return row


def pick_tool_interactive(disabled_tools: Set[str], title_text: str = "Manage Tools") -> bool:
    tools: List[Dict[str, Any]] = []
    disabled = set(disabled_tools)
    for tool in list_tool_catalog():
        tool_copy = dict(tool)
        tool_copy["enabled"] = tool_copy["name"] not in disabled
        tools.append(tool_copy)

    widths = build_tool_table_widths(tools)
    changed = False

    def render_item(tool: Dict[str, Any], index: int, selected: bool = False) -> str:
        return format_tool_entry(index + 1, tool, widths, selected=selected)

    def toggle_tool(tool: Dict[str, Any], _: int) -> None:
        nonlocal changed
        name = str(tool.get("name", ""))
        if bool(tool.get("enabled", True)):
            disabled.add(name)
            tool["enabled"] = False
        else:
            disabled.discard(name)
            tool["enabled"] = True
        changed = True

    interactive_select(
        title_text=title_text,
        items=tools,
        render_item=render_item,
        header_lines=build_tool_table_header(widths),
        footer_lines=[
            "Press Space to toggle the highlighted tool.",
            "Press Enter or Esc to close.",
        ],
        instructions="Use Up/Down, Space to toggle, Enter to close, Esc to cancel.",
        on_space=toggle_tool,
    )
    disabled_tools.clear()
    disabled_tools.update(disabled)
    return changed


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
    for item in items:
        provider_width = max(provider_width, len(str(item.get("provider", ""))))
        name_width = max(name_width, len(str(item.get("name", ""))))
        key_width = max(key_width, len(str(item.get("masked_key", ""))))
    return {
        "provider": min(max(provider_width, 8), 12),
        "name": min(max(name_width, 10), 28),
        "key": min(max(key_width, 10), 24),
    }


def build_api_account_table_header(widths: Dict[str, int]) -> List[str]:
    return [
        f"  {'Id':>2}  {'Provider':<{widths['provider']}}  {'Account':<{widths['name']}}  {'Key':<{widths['key']}}  State",
        f"  {'--':>2}  {'-' * widths['provider']}  {'-' * widths['name']}  {'-' * widths['key']}  -----",
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
        f"{provider:<{widths['provider']}}  "
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
    tavily_accounts: Optional[Dict[str, str]] = None,
    active_api_account: str = "",
    title_text: str = "Manage API Accounts",
) -> Optional[Dict[str, str]]:
    tavily_accounts = tavily_accounts or {}
    items: List[Dict[str, str]] = [{
        "action": "add",
        "provider": "gemini",
        "name": "Add Gemini API",
        "masked_key": "",
        "state": "new",
    }, {
        "action": "add",
        "provider": "tavily",
        "name": "Add Tavily API",
        "masked_key": "",
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
            "state": state,
        })
    for name, key in sorted(tavily_accounts.items(), key=lambda item: item[0].lower()):
        masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
        items.append({
            "action": "load",
            "provider": "tavily",
            "name": name,
            "masked_key": masked,
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
        "state": min(max(state_width, 6), 16),
    }


def build_model_table_header(widths: Dict[str, int]) -> List[str]:
    return [
        f"  {'Id':>2}  {'Model':<{widths['short']}}  {'Full Name':<{widths['name']}}  {'Uses':>4}  {'Tag':<{widths['tag']}}  Cur  {'State':<{widths['state']}}",
        f"  {'--':>2}  {'-' * widths['short']}  {'-' * widths['name']}  {'-' * 4}  {'-' * widths['tag']}  ---  {'-' * widths['state']}",
    ]


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
    if state.startswith("cooldown"):
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
              /help                Show this message
              /exit                Quit
              /reset               Clear conversation history
              /model               Open the model picker
              /test                Test all models and hide failures
              /api                 Open the API account picker
              /loops <n>           Set max tool-call loops
              /tool                Open the tool manager and toggle tools with Space
              /system <text|file>  Replace system instruction or load it from a file
              /save <file>         Save transcript JSON
              /load <file>         Load transcript JSON

            Tips:
              - Prefix a prompt with @file to inject a file's contents into the request.
              - Use /model to pick a model with the arrow keys, or /test to test all models.
              - Use /api to add or switch saved API accounts.
              - Use /tool to see and toggle the implemented local tools.
              - Use /loops to raise or lower the tool-call depth.
            """
        ).strip()
    )


def make_user_content(text: str) -> Dict[str, Any]:
    return {"role": "user", "parts": [{"text": text}]}


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


def resolve_system_instruction_input(text: str, cwd: Path) -> str:
    candidate = resolve_path(text, cwd)
    if candidate.exists() and candidate.is_file():
        content = read_file(candidate)
        if not content.startswith("Error:"):
            return content
    return text


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
    saved_last_model = str(model_prefs.get("last_model") or DEFAULT_MODEL)
    saved_last_api_account = str(model_prefs.get("last_api_account") or "")
    tool_loop_limit = int(model_prefs.get("tool_loop_limit") or DEFAULT_TOOL_LOOPS)
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
    all_tool_names = tool_name_set()

    def snapshot_active_account_model_prefs() -> None:
        if active_api_account:
            api_account_model_prefs[active_api_account] = serialize_model_prefs(
                hidden_models,
                speed_tags,
                model_usage_counts,
            )

    def load_account_model_prefs(account_name: str) -> None:
        nonlocal hidden_models, speed_tags, model_usage_counts
        account_prefs = normalize_account_model_prefs(api_account_model_prefs.get(account_name, {}))
        hidden_models = list(account_prefs.get("hidden_models", []))
        speed_tags = dict(account_prefs.get("speed_tags", {}))
        model_usage_counts = dict(account_prefs.get("model_usage_counts", {}))

    def switch_api_account(account_name: str, key: str) -> None:
        nonlocal active_api_account, api_key
        snapshot_active_account_model_prefs()
        active_api_account = account_name
        api_key = key
        load_account_model_prefs(account_name)

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
    system_instruction = args.system
    contents: List[Dict[str, Any]] = []
    model_cooldowns: Dict[str, dt.datetime] = {}

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

    title("Gemini Terminal CLI")
    info(f"Model: {client.model}")
    if active_api_account:
        info(f"API account: {active_api_account}")
    info(f"Project root: {cwd}")
    info(f"Tools on: {len(enabled_tool_names(disabled_tools))}/{len(all_tool_names)}")
    print_help()

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

    def prompt_text() -> str:
        prune_model_cooldowns()
        prefix = f"gemini-{short_model_label(client.model)}"
        cooldown_text = format_cooldown_until(model_cooldowns.get(client.model))
        if cooldown_text:
            prefix += f" [{cooldown_text}]"
        return _ansi_wrap(f"{prefix}> ", "1;32")

    def persist_selection() -> None:
        account_name = active_api_account or saved_last_api_account
        if account_name:
            api_account_model_prefs[account_name] = serialize_model_prefs(
                hidden_models,
                speed_tags,
                model_usage_counts,
            )
        save_model_prefs(
            hidden_models,
            speed_tags,
            model_usage_counts,
            sorted(disabled_tools),
            client.model,
            account_name,
            tool_loop_limit,
            api_account_model_prefs,
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

    def run_turn(user_text: str) -> None:
        nonlocal contents
        contents.append(make_user_content(user_text))

        for _ in range(tool_loop_limit):
            try:
                response = client.generate(
                    contents=contents,
                    system_instruction=system_instruction,
                    tool_names=enabled_tool_names(disabled_tools),
                    temperature=args.temperature,
                    max_output_tokens=args.max_output_tokens,
                )
            except RuntimeError as exc:
                msg = str(exc).strip()
                error(msg)
                retry_match = re.search(r"Please retry in ([0-9]+(?:\.[0-9]+)?)s", msg, re.IGNORECASE)
                if retry_match:
                    model_cooldowns[client.model] = _now() + dt.timedelta(minutes=1)
                    warn(f"Cooldown set for {client.model}: {format_cooldown_until(model_cooldowns.get(client.model))}")
                if "quota" in msg.lower() or "rate" in msg.lower() or "too many requests" in msg.lower():
                    warn("Try /models and choose a more common chat model like 3.6 flash or 2.5 flash.")
                    write_notification()
                return
            candidates = response.get("candidates", [])
            if not candidates:
                error("Gemini returned no candidates.")
                write_notification()
                return

            content_obj = candidates[0].get("content", {})
            parts = content_obj.get("parts", [])
            text = render_model_parts(parts)
            if text:
                print()
                print(text)
                print()

            function_calls = extract_function_calls(parts)
            if not function_calls:
                contents.append(content_obj)
                record_model_usage(client.model)
                write_notification()
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
                info(format_tool_result(result))

            contents.append({"role": "user", "parts": responses})

        warn(f"Reached the maximum tool-call loop depth ({tool_loop_limit}).")
        write_notification()

    if args.prompt:
        run_turn(args.prompt)
    else:
        command_history: List[str] = []
        while True:
            try:
                user_input = read_dynamic_prompt(prompt_text, command_history).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not user_input:
                continue
            if not command_history or command_history[-1] != user_input:
                command_history.append(user_input)
            if user_input.startswith("/"):
                command, _, remainder = user_input.partition(" ")
                command = command.lower()
                remainder = remainder.strip()

                if command in {"/exit", "/quit"}:
                    break
                if command == "/help":
                    print_help()
                    continue
                if command == "/reset":
                    contents = []
                    info("Conversation cleared.")
                    continue
                if command in {"/model", "/test"}:
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
                            warn("Unknown model selection. Use /model to pick from the list or /test.")
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
                    chosen_api = pick_api_account_interactive(accounts, ensure_tavily_accounts_loaded(), active_api_account)
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
                if command == "/tool":
                    changed = pick_tool_interactive(disabled_tools)
                    if changed:
                        persist_selection()
                        info(f"Tool settings updated. Enabled: {len(enabled_tool_names(disabled_tools))}/{len(all_tool_names)}")
                    continue
                if command == "/system":
                    if remainder:
                        system_instruction = resolve_system_instruction_input(remainder, cwd)
                        loaded_path = resolve_path(remainder, cwd)
                        if loaded_path.exists() and loaded_path.is_file():
                            info(f"System instruction loaded from {loaded_path}")
                        else:
                            info("System instruction replaced.")
                    else:
                        warn("Usage: /system <text|file>")
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

            run_turn(expand_at_file_prompt(user_input, cwd))

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

    persist_selection()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
