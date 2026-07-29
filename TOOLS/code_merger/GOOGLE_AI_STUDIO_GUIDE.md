# 🚀 Code Merger & Google AI Studio Integration Guide

This guide explains how to use **Code Merger** (`merge_gui.py`) with **Google AI Studio's URL Context tool** to bridge your local codebase with AI Studio and merge generated code back to your file system automatically.

---

## 1. Port Configuration (`8999`)

- **Port Changed to `8999`**: The local server built into Code Merger now listens on **port `8999`** instead of `8080` to prevent port conflicts with applications like qBittorrent.

---

## 2. Complete Step-by-Step Workflow

Follow these steps in order when working with Google AI Studio:

```
┌──────────────────────────┐    ┌──────────────────────────┐    ┌──────────────────────────┐
│ 1. Start Tailscale       │ ──>│ 2. Save URL in Settings  │ ──>│ 3. Select Files &        │
│    `tailscale funnel 8999`    │    │    in Code Merger       │    │    Click 🌐 TS Prompt    │
└──────────────────────────┘    └──────────────────────────┘    └──────────────────────────┘
                                                                             │
┌──────────────────────────┐    ┌──────────────────────────┐                 ▼
│ 6. Apply Changes to Disk │ <──│ 5. Parse in MERGE Tab    │ <──│ 4. Run in AI Studio     │
│    (Click ✔ APPLY)       │    │    (Click 🔍 PARSE)      │    │    (Paste & Generate)    │
└──────────────────────────┘    └──────────────────────────┘    └──────────────────────────┘
```

### Step 1: Start Tailscale Funnel First
Open terminal / PowerShell and run:
```bash
tailscale funnel 8999
```
*Tailscale will display your public HTTPS URL (e.g., `https://your-device.tailnet-name.ts.net`). Keep this terminal open while working.*

### Step 2: Configure Code Merger (One-time or per session)
1. Open **Code Merger** (`python merge_gui.py`).
2. Click **⚙ SETTINGS** (top-right).
3. Paste your public Tailscale URL (e.g. `https://your-device.tailnet-name.ts.net`) into the **Tailscale Funnel URL** field and save.

### Step 3: Bundle Code & Generate Prompt (`⚙ PREP Tab`)
1. Open Code Merger and select your project folder/files.
2. Type what you want the AI to do in the **TASK / INSTRUCTIONS** box.
3. Click **🌐 TS** (Tailscale Prompt).
   - Code Merger automatically hosts your bundled codebase at `http://127.0.0.1:8999/codebase` and generates the exact prompt pointing to your public Tailscale URL context.
4. Click **📋 COPY TO CLIPBOARD**.

### Step 4: Run in Google AI Studio
1. Open [Google AI Studio](https://aistudio.google.com).
2. Paste the prompt into AI Studio and hit Send.
3. AI Studio reads your codebase via its **URL Context** tool and generates full file replacements using Markdown File Anchors (e.g., `# FILE: ./src/app.py`).

### Step 5: Merge Changes Back to Disk (`⚡ MERGE Tab`)
1. Copy the output response from Google AI Studio.
2. Switch to the **⚡ MERGE** tab in Code Merger.
3. Paste the AI response into the **AI RESPONSE** text box.
4. Click **🔍 PARSE CHANGES** (automatically detects `# FILE: path`, JSON payloads, or `@@FILE` tokens).
5. Click **✔ APPLY CHANGES** to overwrite local project files (backups are created automatically if `.bak` is enabled).

---

## 3. Alternative: GitHub Gist (No Tunnel Required)

If you don't want to run Tailscale Funnel:
1. Save your **GitHub Token** in **⚙ SETTINGS**.
2. Click **☁️ GIST** in the `⚙ PREP` tab to mirror your codebase to a secret GitHub Gist and copy the prompt.

---

## 4. Supported AI Output Formats

Code Merger parses any of the following schemas automatically when you click **🔍 PARSE CHANGES**:

### Format A: Markdown File Anchors (Recommended)
```markdown
# FILE: src/app.js
```javascript
console.log("Updated code block");
```

// FILE: src/utils.js
```javascript
export const add = (a, b) => a + b;
```
```

### Format B: Structured JSON Payload
```json
{
  "modifications": [
    {
      "filePath": "src/config.json",
      "action": "replace",
      "content": "{\n  \"port\": 8999\n}"
    }
  ]
}
```

### Format C: Standard Code Merger @@ Tokens
```text
@@FILE: src/main.py
@@MODE: replace_file
@@TO:
print("Hello World")
@@END
```

