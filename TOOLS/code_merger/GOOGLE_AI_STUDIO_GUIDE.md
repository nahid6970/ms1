# 🚀 Code Merger & Google AI Studio Integration Guide

This guide explains how to use **Code Merger** (`merge_gui.py`) with **Google AI Studio's URL Context tool** to bridge your local codebase with AI Studio and merge generated code back to your file system automatically.

---

## 1. Overview & Port Configuration

- **Port Changed to `8999`**: The local server built into Code Merger now listens on **port `8999`** instead of `8080` to prevent port conflicts with applications like qBittorrent.
- **Workflow**:
  1. Local Codebase → Bundled by Code Merger → Served via **Tailscale Funnel** (or mirrored to **GitHub Gist**).
  2. Google AI Studio reads the public URL via its **URL Context** tool.
  3. AI Studio outputs modified code using **Markdown Anchors** (`# FILE: path` or `// FILE: path`) or **JSON Payload**.
  4. Code Merger parses the AI output and merges changes directly into your local files.

---

## 2. Setting Up Tailscale Funnel (Port 8999)

To expose your local Code Merger server on port `8999` using Tailscale:

1. **Start Tailscale Funnel on Port 8999**:
   ```bash
   tailscale funnel 8999
   ```
   *(Tailscale will generate a public URL such as `https://your-node.tailscale.net`)*

2. **Save URL in Code Merger**:
   - Open **Code Merger** (`python merge_gui.py`).
   - Click **⚙ SETTINGS** (top-right).
   - Enter your public Tailscale URL (e.g. `https://your-node.tailscale.net`) in the **Tailscale Funnel URL** field and save.

---

## 3. Step-by-Step Usage Guide

### Step 1: Prepare Codebase (`⚙ PREP Tab`)
1. Open Code Merger and select your project directory.
2. Select the files you want to include in the bundle (or click `FULL` / `OUTLINE`).
3. Add your task description into the **TASK / INSTRUCTIONS** box.
4. Click **🌐 TS** (Tailscale Prompt).
   - Code Merger will automatically bundle your code, host it at `http://127.0.0.1:8999/codebase`, and generate the exact prompt containing your Tailscale Funnel URL.
5. Click **📋 COPY TO CLIPBOARD**.

> 💡 *Alternative:* If you don't use Tailscale, set your **GitHub Token** in **⚙ SETTINGS** and click **☁️ GIST** to upload the codebase dump to a secret Gist instead.

---

### Step 2: Generate Code in Google AI Studio
1. Open [Google AI Studio](https://aistudio.google.com).
2. Paste the copied prompt into AI Studio.
3. AI Studio will read the codebase via its **URL Context** tool and generate the full replacement files formatted as Markdown File Anchors (e.g., `# FILE: ./src/app.py`).

---

### Step 3: Automated Merge (`⚡ MERGE Tab`)
1. Copy the output response from Google AI Studio.
2. Switch to the **⚡ MERGE** tab in Code Merger.
3. Paste the AI response into the **AI RESPONSE** input text box.
4. Click **🔍 PARSE CHANGES**:
   - Code Merger automatically detects **Markdown File Anchors** (`# FILE: path` / `// FILE: path`), **Structured JSON Payloads**, or traditional **`@@FILE` tokens**.
5. Click **✔ APPLY CHANGES** to overwrite local project files (backups are created automatically if `.bak` is enabled).

---

## 4. Supported AI Output Formats

Code Merger supports all standard AI Studio output schemas:

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

### Format C: Code Merger @@ Tokens
```text
@@FILE: src/main.py
@@MODE: replace_file
@@TO:
print("Hello World")
@@END
```
