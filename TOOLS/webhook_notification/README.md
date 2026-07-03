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

## Step 1 — Find your Tailscale IP

```
tailscale ip -4
```

You'll get something like `100.x.x.x`. Use this IP everywhere below instead of `localhost`
when sending from another device, a browser AI agent, or over the internet.

---

## Step 2 — Start the server

Double-click `start.bat`, or:

```
python server.py
```

Server runs on `http://0.0.0.0:5050` — it listens on ALL interfaces including Tailscale automatically.

### Firewall (do this once if connections from other devices time out)

Run in an elevated PowerShell:

```powershell
New-NetFirewallRule -DisplayName "Webhook Notify" -Direction Inbound -Protocol TCP -LocalPort 5050 -Action Allow
```

---

## Use Case 1 — Webhook from any script or tool

### Send a notification

**curl:**
```bash
curl -X POST http://100.x.x.x:5050/notify \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Deploy Done\", \"message\": \"v2.3.1 deployed to prod.\", \"source\": \"CI/CD\"}"
```

**Python:**
```python
import requests
requests.post("http://100.x.x.x:5050/notify", json={
    "title": "Task Complete",
    "message": "The scraper finished. 1,200 rows collected.",
    "source": "my-script"
})
```

**Plain text (simplest):**
```bash
curl -X POST http://100.x.x.x:5050/notify -d "Build finished!"
```

**Browser address bar (quick test):**
```
http://localhost:5050/notify?message=Hello+World
```

### JSON fields

| Field | Required | Default | Description |
|---|---|---|---|
| `title` | No | `"Webhook Notification"` | Popup title |
| `message` | **Yes** | — | Main text shown in popup |
| `source` | No | `"webhook"` | Small label shown below message |
| `token` | If auth on | — | Auth token (see Security section) |

---

## Use Case 2 — Web AI Agents (ChatGPT, Claude, Gemini, etc.)

Web agents can't run code on your machine, but there are a few ways to make them send notifications.

---

### Option A — Tell them to give you the curl (always works, zero setup)

Paste this at the start of any chat:

> *"When you finish this task, give me a ready-to-run curl command that sends a POST request
> to `http://100.x.x.x:5050/notify` with a JSON body:
> `{"title": "Done", "message": "<your summary>", "source": "<your name>"}`
> I will run it to get a desktop notification."*

The agent outputs the curl → you copy-paste it in your terminal → popup appears.

---

### Option B — ChatGPT Custom GPT with an Action (fires automatically)

If you use **Custom GPTs**, you can give it a real HTTP action so it fires the webhook itself.

1. Go to **ChatGPT → Explore GPTs → Create → Configure → Add Actions**
2. Paste this schema (replace `100.x.x.x` with your Tailscale IP):

```yaml
openapi: 3.1.0
info:
  title: Desktop Notify
  version: 1.0.0
servers:
  - url: http://100.x.x.x:5050
paths:
  /notify:
    post:
      operationId: sendNotification
      summary: Send a desktop notification popup
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                title:
                  type: string
                message:
                  type: string
                source:
                  type: string
              required: [message]
      responses:
        '200':
          description: Notification sent
```

3. In the GPT's **system prompt** add:
   > *"When you have finished a task, call `sendNotification` with a brief summary as the message."*

Now the GPT fires the popup automatically without you doing anything.

---

### Option C — Claude Projects (system prompt trick)

Claude.ai can't make HTTP requests directly, but you can make it reliably output the command.

Add this to your **Project Instructions** in Claude:

> *"When you have completely finished helping the user, output a ready-to-run curl block
> at the end of your response:*
> ```
> curl -X POST http://100.x.x.x:5050/notify -H "Content-Type: application/json" -d "{\"title\":\"Done\",\"message\":\"SUMMARY_HERE\",\"source\":\"Claude\"}"
> ```
> *Replace SUMMARY_HERE with a one-line summary of what you did."*

Claude will output it at the end of every task. One click to copy, one paste to run.

---

### Option D — Any agent that supports tool use / function calling

Give the agent this function definition (works for any framework that supports tool use):

```json
{
  "name": "notify_user",
  "description": "Send a desktop notification popup to the user's Windows machine. Call this when a task is complete.",
  "parameters": {
    "type": "object",
    "properties": {
      "title":   { "type": "string", "description": "Short title" },
      "message": { "type": "string", "description": "Summary of what was done" },
      "source":  { "type": "string", "description": "Your name or system name" }
    },
    "required": ["message"]
  }
}
```

Then implement it with:
```python
import requests
def notify_user(title="Done", message="", source="Agent"):
    requests.post("http://100.x.x.x:5050/notify", json={
        "title": title, "message": message, "source": source
    })
```

---

## Use Case 3 — Local MCP Agents (Kiro, Claude Desktop, etc.)

The MCP server (`mcp_server.py`) lets local agents send popups **directly** — no HTTP server needed, no network involved. Pure subprocess call over stdio.

### Setup for Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "desktop-notify": {
      "command": "python",
      "args": ["C:/full/path/to/webhook_notification/mcp_server.py"]
    }
  }
}
```

### Setup for Kiro or other MCP clients

Same pattern — point `command` to `python` and `args` to the full path of `mcp_server.py`.

### Available MCP tools

| Tool | Arguments | Description |
|---|---|---|
| `notify` | `title`, `message`, `source` | Show a popup with custom content |
| `notify_task_complete` | `summary`, `agent_name` | Shorthand "Task Complete" popup |

### Tell your agent to use it

Add to your system prompt or at the start of a conversation:

> *"When you finish a task, call the `notify_task_complete` tool with a brief summary of what you did."*

---

## Direct popup — no server needed

```bash
python notify.py "Title" "Message body" "Source label"
python notify.py "Build Done" "All tests passed." "pytest"
python notify.py
```

---

## Security

### Do you need a token?

| Scenario | Recommendation |
|---|---|
| Only you, over Tailscale | No token needed — Tailscale is already private |
| You share your Tailscale network | Set a token |
| Server exposed to the public internet | Definitely set a token |

### Setting a token

Edit `config.json`:
```json
{
  "auth_token": "my-secret-token-here"
}
```

Then include it in requests one of three ways:

```bash
# Authorization header
curl -H "Authorization: Bearer my-secret-token-here" ...

# JSON body field
{"message": "done", "token": "my-secret-token-here"}

# Query param
http://100.x.x.x:5050/notify?token=my-secret-token-here&message=done
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

Auto-created on first run. Edit and restart the server to apply changes.

---

## Logs

All notifications are logged to `notifications.log` in the same folder.
