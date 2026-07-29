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
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.history import InMemoryHistory
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
    CompleteStyle = None
    Style = None

# --- Re-use all utility functions (read_file, fuzzy_patch, etc.) exactly from Gemini CLI ---
# [Note to user: These are identical to gemini_cli.py functions for local file ops]

def _now_stamp() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d-%H:%M")

def write_notification() -> None:
    try:
        NOTIFICATION_FILE.write_text(_now_stamp(), encoding="utf-8")
    except Exception: pass

def _ansi_wrap(text: str, code: str) -> str:
    if not sys.stdout.isatty(): return text
    return f"\033[{code}m{text}\033[0m"

def info(text: str) -> None: print(_ansi_wrap(text, "36"))
def warn(text: str) -> None: print(_ansi_wrap(text, "33"))
def error(text: str) -> None: print(_ansi_wrap(text, "31"))
def title(text: str) -> None: print(_ansi_wrap(text, "1;35"))

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

def list_directory(path: Path) -> str:
    try:
        if not path.is_dir(): return f"Error: {path} is not a directory."
        entries = [f"{item.name}{'/' if item.is_dir() else ''}" for item in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))]
        return "\n".join(entries) if entries else "Empty."
    except Exception as exc: return str(exc)

def run_powershell_command(command: str, cwd: Path, timeout: int = 60) -> str:
    try:
        result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command], cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return ((result.stdout or "") + (result.stderr or "")).strip() or f"Done (exit {result.returncode})"
    except Exception as exc: return str(exc)

# --- GROQ CLIENT (OpenAI Compatible) ---

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
        
        # Build payload with system message if provided
        history = []
        if system_instruction:
            history.append({"role": "system", "content": system_instruction})
        history.extend(messages)

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": history,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        # IMPORTANT: Added User-Agent to avoid Error 1010
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GroqCLI/1.0"
            },
            method="POST",
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
        request = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self.api_key}", "User-Agent": "GroqCLI/1.0"},
            method="GET"
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("data", [])

# --- Interaction Logic (Ported from Gemini CLI) ---

def execute_tool(name: str, args: Dict[str, Any], cwd: Path) -> str:
    # This is where you link the OpenAI-style tool calls to your utility functions
    if name == "read_file": return read_file(resolve_path(args.get("filepath", ""), cwd))
    if name == "list_directory": return list_directory(resolve_path(args.get("path", "."), cwd))
    if name == "run_powershell": return run_powershell_command(args.get("command", ""), cwd)
    # Add other tools here...
    return f"Tool {name} not implemented yet in Groq version."

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default=os.environ.get("GROQ_API_KEY"))
    args = parser.parse_args()

    # Load prefs, history, etc. (Omitted for brevity, but use logic from gemini_cli.py)
    # Initial setup for interactive loop
    api_key = args.api_key
    if not api_key:
        error("No API key found. Use --api-key or set GROQ_API_KEY env var.")
        return 1

    client = GroqClient(api_key, DEFAULT_MODEL)
    messages: List[Dict[str, Any]] = []
    cwd = Path.cwd()
    
    # Load Tools
    tools = None
    if TOOLS_FILE.exists():
        try: tools = json.loads(TOOLS_FILE.read_text(encoding="utf-8"))
        except: pass

    title("Groq Terminal CLI")
    info(f"Model: {DEFAULT_MODEL} | Root: {cwd}")

    while True:
        try:
            # Using basic input here for simplicity, but prompt_toolkit is better
            user_input = input(_ansi_wrap("groq> ", "1;32")).strip()
        except (EOFError, KeyboardInterrupt): break

        if not user_input: continue

        # --- Slash Command Interceptor ---
        if user_input.startswith("/"):
            cmd = user_input.split()[0].lower()
            if cmd == "/exit": break
            if cmd == "/reset":
                messages = []
                info("Conversation reset.")
                continue
            if cmd == "/help":
                print("Commands: /exit, /reset, /help")
                continue
            # If command not handled, notify user
            warn(f"Command {cmd} is not yet implemented in the Groq version.")
            continue

        # --- Standard Chat Turn ---
        messages.append({"role": "user", "content": user_input})
        
        for _ in range(DEFAULT_TOOL_LOOPS):
            try:
                response = client.generate(messages, system_instruction=DEFAULT_SYSTEM, tools=tools)
            except Exception as e:
                error(str(e))
                break
                
            choice = response["choices"][0]
            msg = choice["message"]
            messages.append(msg)
            
            if msg.get("content"):
                print(f"\n{msg['content']}\n")
            
            if not msg.get("tool_calls"):
                write_notification()
                break
                
            for tool_call in msg["tool_calls"]:
                t_id = tool_call["id"]
                t_name = tool_call["function"]["name"]
                t_args = json.loads(tool_call["function"]["arguments"])
                
                info(f"[tool] {t_name}({t_args})")
                result = execute_tool(t_name, t_args, cwd)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": t_id,
                    "content": result
                })
                info(f"[result] {result[:100]}...")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
