"""
mcp_server.py — MCP (Model Context Protocol) server for desktop notifications.

Local AI agents (Kiro, Claude Desktop, etc.) can call the `notify` tool to
send a desktop popup directly — no HTTP involved, pure subprocess call.

Usage (stdio mode, for MCP clients):
    python mcp_server.py

Add to your MCP config (e.g. Claude Desktop):
    {
      "mcpServers": {
        "desktop-notify": {
          "command": "python",
          "args": ["C:/path/to/mcp_server.py"]
        }
      }
    }
"""

import sys
import json
import subprocess
import threading
from pathlib import Path

# ── MCP over stdio ─────────────────────────────────────────────────────────
# Implements a minimal MCP server (JSON-RPC 2.0) over stdin/stdout.
# No external MCP SDK required — stdlib only.

BASE_DIR      = Path(__file__).parent
NOTIFY_SCRIPT = BASE_DIR / "notify.py"
PYTHON_EXE    = sys.executable

# ── Tool definitions ──────────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "notify",
        "description": (
            "Send a desktop notification popup on the user's Windows machine. "
            "Call this when a task is complete, an error occurs, or you need "
            "to alert the user of something important."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short title for the notification (e.g. 'Task Complete')",
                    "default": "Agent Notification"
                },
                "message": {
                    "type": "string",
                    "description": "The notification body text."
                },
                "source": {
                    "type": "string",
                    "description": "Name of the agent or system sending the notification.",
                    "default": "MCP Agent"
                }
            },
            "required": ["message"]
        }
    },
    {
        "name": "notify_task_complete",
        "description": (
            "Convenience tool — send a 'Task Complete' notification. "
            "Call this at the end of a task or workflow."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Brief summary of what was completed.",
                    "default": "Task finished successfully."
                },
                "agent_name": {
                    "type": "string",
                    "description": "Name of the agent (shown as source).",
                    "default": "Agent"
                }
            }
        }
    }
]


def _launch_popup(title: str, message: str, source: str):
    """Fire-and-forget popup launch."""
    try:
        subprocess.Popen(
            [PYTHON_EXE, str(NOTIFY_SCRIPT), title, message, source],
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except Exception as e:
        return str(e)
    return None


def handle_notify(args: dict) -> dict:
    title   = str(args.get("title",   "Agent Notification"))
    message = str(args.get("message", ""))
    source  = str(args.get("source",  "MCP Agent"))

    if not message:
        return {"isError": True, "content": [{"type": "text", "text": "message is required"}]}

    err = _launch_popup(title, message, source)
    if err:
        return {"isError": True, "content": [{"type": "text", "text": f"Error: {err}"}]}

    return {
        "content": [{
            "type": "text",
            "text": f"✓ Notification sent: [{source}] {title}: {message}"
        }]
    }


def handle_notify_task_complete(args: dict) -> dict:
    summary    = str(args.get("summary",    "Task finished successfully."))
    agent_name = str(args.get("agent_name", "Agent"))
    return handle_notify({
        "title":   "✅ Task Complete",
        "message": summary,
        "source":  agent_name,
    })


TOOL_HANDLERS = {
    "notify":               handle_notify,
    "notify_task_complete": handle_notify_task_complete,
}


# ── JSON-RPC helpers ──────────────────────────────────────────────────────────

def send(obj: dict):
    line = json.dumps(obj, ensure_ascii=False)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def respond(req_id, result):
    send({"jsonrpc": "2.0", "id": req_id, "result": result})


def error_response(req_id, code: int, message: str):
    send({"jsonrpc": "2.0", "id": req_id,
          "error": {"code": code, "message": message}})


# ── Request dispatch ──────────────────────────────────────────────────────────

def dispatch(msg: dict):
    method = msg.get("method", "")
    req_id = msg.get("id")
    params = msg.get("params", {})

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    if method == "initialize":
        respond(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "desktop-notify",
                "version": "1.0.0"
            }
        })
        return

    if method == "notifications/initialized":
        return   # no response for notifications

    # ── Tools ─────────────────────────────────────────────────────────────────
    if method == "tools/list":
        respond(req_id, {"tools": TOOLS})
        return

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        handler   = TOOL_HANDLERS.get(tool_name)

        if handler is None:
            error_response(req_id, -32601, f"Unknown tool: {tool_name}")
            return

        result = handler(arguments)
        respond(req_id, result)
        return

    # Unknown method
    if req_id is not None:
        error_response(req_id, -32601, f"Method not found: {method}")


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    # Unbuffered stdout for MCP clients
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            msg = json.loads(raw_line)
        except json.JSONDecodeError:
            send({"jsonrpc": "2.0", "id": None,
                  "error": {"code": -32700, "message": "Parse error"}})
            continue

        try:
            dispatch(msg)
        except Exception as ex:
            req_id = msg.get("id")
            if req_id is not None:
                error_response(req_id, -32603, f"Internal error: {ex}")


if __name__ == "__main__":
    main()
