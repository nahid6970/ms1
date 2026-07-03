# Webhook Notification Server

A self-hosted webhook server that shows cyberpunk-style desktop popups on Windows.  
No external services, no accounts, no rate limits. 100% local.

---

## Files

| File | Purpose |
|---|---|
| `server.py` | Flask HTTP server — receives POST requests and shows popups |
| `notify.py` | PyQt6 popup window (can also be called directly) |
| `mcp_server.py` | MCP server — local AI agents call this directly via stdio |
| `config.json` | Auto-created on first run. Set token, port, etc. |
| `start.bat` | Double-click launcher for the server |

---

## Install

```
pip install -r requirements.txt
```

---

## Use Case 1 — Webhook from any HTTP client

### Start the server

```
start.bat
```
or
```
python server.py
```

Server runs on `http://0.0.0.0:5050` by default.

### Send a notification

**curl:**
```bash
curl -X POST http://<your-ip>:5050/notify \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Deploy Done\", \"message\": \"v2.3.1 deployed to prod.\", \"source\": \"CI/CD\"}"
```

**Python:**
```python
import requests
requests.post("http://<your-ip>:5050/notify", json={
    "title": "Task Complete",
    "message": "The scraper finished. 1,200 rows collected.",
    "source": "my-script"
})
```

**Plain text body (simplest):**
```bash
curl -X POST http://<your-ip>:5050/notify -d "Build finished!"
```

**Browser (GET) — for quick tests:**
```
http://localhost:5050/notify?message=Hello+World
```

### JSON fields

| Field | Required | Default | Description |
|---|---|---|---|
| `title` | No | `"Webhook Notification"` | Popup title |
| `message` | **Yes** | — | Main text shown in popup |
| `source` | No | `"webhook"` | Label shown below message |
| `token` | If auth on | — | Auth token (see Security) |

---

## Use Case 2 — Web AI Agent (ChatGPT, Claude web, Gemini, etc.)

Web AI agents can't run local code, but they can make HTTP requests using their
action/tool features, or you can give them this exact instruction to paste:

> **Paste this into the AI chat to give it the webhook URL:**
>
> *"When you have finished this task, send a POST request to:*
> *`http://<your-tailscale-ip>:5050/notify`*
> *with JSON body: `{"title": "Task Complete", "message": "<your summary here>", "source": "ChatGPT"}`*
> *This will show a desktop notification on my PC."*

### With Tailscale

Your Tailscale IP is stable (e.g. `100.x.x.x`). Use it instead of `localhost` when
sending from another device or network.

To find your Tailscale IP:
```
tailscale ip -4
```

### Security for public access

Set a token in `config.json`:
```json
{
  "auth_token": "my-secret-token-here"
}
```

Then include it in requests:
```bash
curl -X POST http://<ip>:5050/notify \
  -H "Authorization: Bearer my-secret-token-here" \
  -d "{\"message\": \"done\"}"
```

Or in the JSON body:
```json
{"message": "done", "token": "my-secret-token-here"}
```

---

## Use Case 3 — Local MCP Agent (Kiro, Claude Desktop, etc.)

The MCP server (`mcp_server.py`) lets local AI agents send popups directly
without needing the HTTP server running.

### Claude Desktop config
Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "desktop-notify": {
      "command": "python",
      "args": ["C:/path/to/webhook_notification/mcp_server.py"]
    }
  }
}
```

### Kiro / other MCP clients
Add to your agent's MCP settings the same way — point `command` to `python`
and `args` to the full path of `mcp_server.py`.

### Available MCP tools

| Tool | Description |
|---|---|
| `notify` | Show a popup with `title`, `message`, `source` |
| `notify_task_complete` | Shorthand — sends "Task Complete" with a `summary` |

### Tell your agent to use it
Add this to your system prompt or at the start of a conversation:
> *"When you finish a task, call the `notify_task_complete` tool with a brief summary."*

---

## Direct popup (no server needed)

```bash
python notify.py "Title" "Message body" "Source label"
python notify.py "Build Done" "All tests passed." "pytest"
python notify.py  # shows a test popup
```

---

## config.json reference

```json
{
  "host": "0.0.0.0",
  "port": 5050,
  "auth_token": "",
  "log_notifications": true,
  "default_title": "Webhook Notification",
  "default_source": "webhook"
}
```

Leave `auth_token` empty if you're only using this over Tailscale (already private).

---

## Logs

All notifications are logged to `notifications.log` in the same folder.
