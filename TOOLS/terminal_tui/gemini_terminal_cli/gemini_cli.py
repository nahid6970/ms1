#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import subprocess
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_SYSTEM = (
    "You are a terminal coding assistant. "
    "Be concise, practical, and ask before making destructive changes."
)
MAX_TOOL_LOOPS = 8
MAX_TEXT_CHARS = 12000
DEFAULT_MODEL_LIST_LIMIT = 12
MODELS_PAGE_SIZE = 1000
MODEL_PREFS_FILE = Path(__file__).with_name("model_prefs.json")


def _now_stamp() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d-%H:%M")


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


def execute_tool(name: str, args: Dict[str, Any], cwd: Path) -> str:
    if name == "read_file":
        filepath = args.get("filepath", "")
        return read_file(resolve_path(filepath, cwd))
    if name == "write_file":
        filepath = args.get("filepath", "")
        content = args.get("content", "")
        return write_file(resolve_path(filepath, cwd), content)
    if name == "delete_file":
        filepath = args.get("filepath", "")
        return delete_path(resolve_path(filepath, cwd))
    if name == "list_directory":
        path = args.get("path", ".")
        return list_directory(resolve_path(path, cwd))
    if name == "get_system_info":
        return get_system_info(cwd)
    if name == "run_shell_command":
        return run_shell_command(str(args.get("command", "")), cwd)
    if name == "request_follow_up":
        reason = args.get("reason") or "Continuing..."
        return f"Follow-up turn granted: {reason}"
    return f"Unknown tool: {name}"


class GeminiClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(
        self,
        contents: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        tools_enabled: bool = True,
        temperature: float = 0.2,
        max_output_tokens: int = 2048,
    ) -> Dict[str, Any]:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{urllib.parse.quote(self.model, safe='')}:generateContent?key={urllib.parse.quote(self.api_key)}"
        )
        payload: Dict[str, Any] = {"contents": contents}
        if tools_enabled:
            payload["tools"] = [{"functionDeclarations": list(FUNCTIONS.values())}]
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


def render_model_parts(parts: List[Dict[str, Any]]) -> str:
    chunks: List[str] = []
    for part in parts:
        if "text" in part:
            chunk = normalize_text(str(part["text"]))
            if chunk:
                chunks.append(chunk)
    return "\n\n".join(chunks).strip()


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


def load_model_prefs() -> Dict[str, Any]:
    if not MODEL_PREFS_FILE.exists():
        return {"hidden_models": []}
    try:
        data = json.loads(MODEL_PREFS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"hidden_models": []}
        hidden = data.get("hidden_models", [])
        if not isinstance(hidden, list):
            hidden = []
        return {"hidden_models": [str(item) for item in hidden]}
    except Exception:
        return {"hidden_models": []}


def save_model_prefs(hidden_models: List[str]) -> str:
    payload = {"hidden_models": sorted(set(hidden_models))}
    MODEL_PREFS_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"Saved model preferences to {MODEL_PREFS_FILE}"


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


def format_model_entry(index: int, model: Dict[str, Any], current_model: str) -> str:
    name = model_name(model)
    display_name = short_model_name(model)
    active = " *" if name == current_model else ""
    hidden = " (hidden)" if model.get("_hidden") else ""
    return f"{index:>2}. {display_name} [{name}]{hidden}{active}"


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
        tools_enabled=False,
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
              /models              List recommended chat models
              /models all          List the full catalog
              /models hide <x>     Hide a model from the default list
              /models show <x>     Unhide a model
              /models hidden       List hidden models
              /models test <x>     Run a quick test on a model
              /model <name>        Switch Gemini model
              /model <number>      Switch using the /models list
              /system <text>       Replace system instruction
              /tools on|off        Enable or disable local tools
              /save <file>         Save transcript JSON
              /load <file>         Load transcript JSON

            Tips:
              - Prefix a prompt with @file to inject a file's contents into the request.
              - Use normal chat for everything else.
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Gemini terminal CLI")
    parser.add_argument("-p", "--prompt", help="Run one prompt and exit")
    parser.add_argument("--api-key", default=os.environ.get("GEMINI_API_KEY", ""), help="Gemini API key")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini model")
    parser.add_argument("--system", default=DEFAULT_SYSTEM, help="System instruction")
    parser.add_argument("--project-root", default=os.getcwd(), help="Working directory for local tools")
    parser.add_argument("--temperature", type=float, default=0.2, help="Generation temperature")
    parser.add_argument("--max-output-tokens", type=int, default=2048, help="Max output tokens")
    parser.add_argument("--no-tools", action="store_true", help="Disable local tool calling")
    parser.add_argument("--load-transcript", help="Load transcript JSON at startup")
    parser.add_argument("--save-transcript", help="Auto-save transcript on exit")
    args = parser.parse_args()

    if not args.api_key:
        error("Missing Gemini API key. Set GEMINI_API_KEY or pass --api-key.")
        return 1

    cwd = resolve_path(args.project_root, Path.cwd())
    if not cwd.exists():
        error(f"Project root does not exist: {cwd}")
        return 1

    client = GeminiClient(args.api_key, args.model)
    system_instruction = args.system
    tools_enabled = not args.no_tools
    contents: List[Dict[str, Any]] = []
    model_prefs = load_model_prefs()
    hidden_models: List[str] = list(model_prefs.get("hidden_models", []))

    if args.load_transcript:
        transcript_path = resolve_path(args.load_transcript, Path.cwd())
        loaded = load_transcript(transcript_path)
        system_instruction = loaded.get("system_instruction", system_instruction)
        client.model = loaded.get("model", client.model)
        tools_enabled = bool(loaded.get("tools_enabled", tools_enabled))
        cwd = resolve_path(loaded.get("project_root", str(cwd)), Path.cwd())
        contents = list(loaded.get("contents", []))

    title("Gemini Terminal CLI")
    info(f"Model: {client.model}")
    info(f"Project root: {cwd}")
    info(f"Tools: {'on' if tools_enabled else 'off'}")
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
        shown_models = filter_models_for_display(models, hidden_models, show_all=show_all)
        print()
        title("Available Models")
        if show_all:
            print(f"Showing full catalog: {len(shown_models)} models. Current model: {client.model}")
        else:
            print(f"Showing recommended models: {len(shown_models)} models. Current model: {client.model}")
        print()
        if show_all:
            index = 1
            for group in ("Stable", "Aliases", "Preview", "Gemma", "Image"):
                grouped_models = [m for m in shown_models if model_group(m) == group]
                if not grouped_models:
                    continue
                print(f"[{group}]")
                for model in grouped_models:
                    print(format_model_entry(index, model, client.model))
                    index += 1
                print()
        else:
            for index, model in enumerate(shown_models[:DEFAULT_MODEL_LIST_LIMIT], start=1):
                print(format_model_entry(index, model, client.model))
            if len(shown_models) > DEFAULT_MODEL_LIST_LIMIT:
                print()
                print("Tip: use /models all for the full catalog.")
        print()

    def run_turn(user_text: str) -> None:
        nonlocal contents
        contents.append(make_user_content(user_text))

        for _ in range(MAX_TOOL_LOOPS):
            try:
                response = client.generate(
                    contents=contents,
                    system_instruction=system_instruction,
                    tools_enabled=tools_enabled,
                    temperature=args.temperature,
                    max_output_tokens=args.max_output_tokens,
                )
            except RuntimeError as exc:
                msg = str(exc).strip()
                error(msg)
                if "quota" in msg.lower() or "rate" in msg.lower() or "too many requests" in msg.lower():
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
                info(f"[tool] {name} {json.dumps(call_args, ensure_ascii=False)}")
                result = execute_tool(name, call_args, cwd)
                responses.append(
                    {
                        "functionResponse": {
                            "name": name,
                            "response": {"result": result},
                        }
                    }
                )
                info(f"[tool-result] {result[:4000]}")

            contents.append({"role": "user", "parts": responses})

        warn("Reached the maximum tool-call loop depth.")

    if args.prompt:
        run_turn(args.prompt)
    else:
        while True:
            try:
                user_input = input(_ansi_wrap("gemini> ", "1;32")).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not user_input:
                continue
            if user_input.startswith("/"):
                command, _, remainder = user_input.partition(" ")
                command = command.lower()
                remainder = remainder.strip()

                if command in {"/exit", "/quit"}:
                    break
                if command == "/help":
                    print_help()
                    continue
                if command == "/models":
                    subcommand, _, subargs = remainder.partition(" ")
                    subcommand = subcommand.lower().strip()
                    subargs = subargs.strip()
                    if not subcommand:
                        print_model_list(show_all=False)
                    elif subcommand in {"all", "full"}:
                        print_model_list(show_all=True)
                    elif subcommand == "hidden":
                        hidden_list = [m for m in (model_cache or refresh_model_cache()) if model_name(m) in hidden_models]
                        if not hidden_list:
                            info("No hidden models.")
                        else:
                            print()
                            title("Hidden Models")
                            for index, model in enumerate(hidden_list, start=1):
                                print(format_model_entry(index, model, client.model))
                            print()
                    elif subcommand in {"hide", "show", "test"}:
                        if not subargs:
                            warn(f"Usage: /models {subcommand} <name|number>")
                            continue
                        if not model_cache:
                            refresh_model_cache()
                        chosen = choose_model_from_list(model_cache, subargs)
                        if not chosen:
                            warn("Unknown model selection. Use /models first, then a number or model name.")
                            continue
                        if subcommand == "hide":
                            if chosen not in hidden_models:
                                hidden_models.append(chosen)
                                print(save_model_prefs(hidden_models))
                            info(f"Hidden: {chosen}")
                        elif subcommand == "show":
                            if chosen in hidden_models:
                                hidden_models = [m for m in hidden_models if m != chosen]
                                print(save_model_prefs(hidden_models))
                            info(f"Shown: {chosen}")
                        else:
                            try:
                                result = test_model(client, chosen, temperature=0.0)
                                info(f"Test ok: {chosen}")
                                print(result)
                            except RuntimeError as exc:
                                error(f"Test failed for {chosen}: {exc}")
                    else:
                        warn("Usage: /models [all|hidden|hide <x>|show <x>|test <x>]")
                    continue
                if command == "/reset":
                    contents = []
                    info("Conversation cleared.")
                    continue
                if command == "/model":
                    if remainder:
                        if not model_cache:
                            refresh_model_cache()
                        chosen = choose_model_from_list(model_cache, remainder)
                        if chosen:
                            client.model = chosen
                            info(f"Model set to {client.model}")
                        else:
                            warn("Unknown model selection. Use /models first, then /model <number> or /model <name>.")
                    else:
                        warn("Usage: /model <name>")
                    continue
                if command == "/system":
                    if remainder:
                        system_instruction = remainder
                        info("System instruction replaced.")
                    else:
                        warn("Usage: /system <text>")
                    continue
                if command == "/tools":
                    if remainder.lower() in {"on", "off"}:
                        tools_enabled = remainder.lower() == "on"
                        info(f"Tools {'enabled' if tools_enabled else 'disabled'}.")
                    else:
                        warn("Usage: /tools on|off")
                    continue
                if command == "/save":
                    if remainder:
                        transcript_path = resolve_path(remainder, Path.cwd())
                        state = {
                            "model": client.model,
                            "system_instruction": system_instruction,
                            "project_root": str(cwd),
                            "tools_enabled": tools_enabled,
                            "contents": contents,
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
                        tools_enabled = bool(loaded.get("tools_enabled", tools_enabled))
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
            "tools_enabled": tools_enabled,
            "contents": contents,
        }
        print(save_transcript(transcript_path, state))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
