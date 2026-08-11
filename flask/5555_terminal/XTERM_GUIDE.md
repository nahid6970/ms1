# Interactive Web Terminal with xterm.js + node-pty (Windows)

Full PTY support — runs kiro-cli, gemini REPL, and any interactive CLI natively in the browser, with the same dark green theme as the existing Flask terminal.

---

## Prerequisites

- Node.js 18+ installed
- Windows 10/11 (ConPTY support built-in)
- Visual Studio Build Tools (required to compile `node-pty`)

Install build tools if you don't have them:
```
npm install --global windows-build-tools
```
Or install "Desktop development with C++" from [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

---

## Project Setup

```
mkdir pty-terminal
cd pty-terminal
npm init -y
npm install node-pty ws express
```

---

## File Structure

```
pty-terminal/
├── server.js
└── public/
    └── index.html
```

---

## server.js

```js
const express = require('express');
const { WebSocketServer } = require('ws');
const pty = require('node-pty');
const path = require('path');

const app = express();
app.use(express.static(path.join(__dirname, 'public')));

const server = app.listen(5556, '0.0.0.0', () => {
  const { networkInterfaces } = require('os');
  const nets = networkInterfaces();
  let localIP = 'localhost';
  for (const iface of Object.values(nets).flat()) {
    if (iface.family === 'IPv4' && !iface.internal) { localIP = iface.address; break; }
  }
  console.log(`PTY Terminal running at:`);
  console.log(`  Local:   http://localhost:5556`);
  console.log(`  Network: http://${localIP}:5556`);
});

const wss = new WebSocketServer({ server });

wss.on('connection', (ws) => {
  const shell = pty.spawn('powershell.exe', [], {
    name: 'xterm-256color',
    cols: 120,
    rows: 30,
    cwd: process.env.USERPROFILE,
    env: {
      ...process.env,
      // Add any extra CLI paths here
      PATH: process.env.PATH + ';C:\\Users\\nahid\\AppData\\Local\\Kiro-Cli'
    }
  });

  // PTY output → browser
  shell.onData((data) => ws.send(JSON.stringify({ type: 'output', data })));

  // Browser input → PTY
  ws.on('message', (msg) => {
    const { type, data, cols, rows } = JSON.parse(msg);
    if (type === 'input') shell.write(data);
    if (type === 'resize') shell.resize(cols, rows);
  });

  ws.on('close', () => shell.kill());
});
```

---

## public/index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, interactive-widget=resizes-content, user-scalable=no">
  <title>PowerShell Web Terminal</title>
  <link rel="icon" type="image/png" href="https://upload.wikimedia.org/wikipedia/commons/a/af/PowerShell_Core_6.0_icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      background: #0a0a0f;
      color: #e0e0e0;
      font-family: 'JetBrains Mono', 'Consolas', monospace;
      height: 100vh;
      height: 100dvh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background-image:
        radial-gradient(ellipse at 15% 50%, rgba(0,255,170,0.04) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 20%, rgba(0,180,255,0.04) 0%, transparent 55%);
    }

    .terminal-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 10px;
      overflow: hidden;
      gap: 10px;
      min-height: 0;
    }

    .output-wrapper {
      flex: 1;
      position: relative;
      min-height: 0;
      background: #05050a;
      border: 1px solid #00ffaa18;
      border-radius: 6px;
      padding: 8px;
      box-shadow: inset 0 0 40px rgba(0,0,0,0.6);
      overflow: hidden;
    }

    /* xterm.js fills the wrapper */
    #terminal { width: 100%; height: 100%; }
    .xterm { height: 100%; }
    .xterm-viewport { border-radius: 6px; }

    /* Match scrollbar style */
    .xterm-viewport::-webkit-scrollbar { width: 5px; }
    .xterm-viewport::-webkit-scrollbar-track { background: transparent; }
    .xterm-viewport::-webkit-scrollbar-thumb { background: #00ffaa22; border-radius: 3px; }
    .xterm-viewport::-webkit-scrollbar-thumb:hover { background: #00ffaa55; }

    .status-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      background: #0d1117;
      border: 1px solid #ffffff1a;
      border-radius: 6px;
      padding: 6px 12px;
      flex-shrink: 0;
      font-size: 12px;
      color: #444;
    }

    .status-dot {
      width: 7px; height: 7px;
      border-radius: 50%;
      background: #ff4466;
      flex-shrink: 0;
    }
    .status-dot.connected { background: #00ffaa; box-shadow: 0 0 6px #00ffaa88; }

    .status-bar span { margin-right: auto; }

    .btn {
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-family: inherit;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 28px; height: 28px;
      transition: all 0.15s;
      background: #0d1117;
      border: 1px solid #ffffff1a;
      color: #555;
      padding: 0;
    }
    .btn:hover { border-color: #00ffaa44; color: #00ffaa; background: #0d1a14; }
  </style>
</head>
<body>
  <div class="terminal-container">
    <div class="output-wrapper">
      <div id="terminal"></div>
    </div>
    <div class="status-bar">
      <div class="status-dot" id="status-dot"></div>
      <span id="status-text">Connecting...</span>
      <button class="btn" id="reconnect-btn" title="Reconnect">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"></polyline>
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
        </svg>
      </button>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>
  <script>
    const term = new Terminal({
      fontFamily: "'JetBrains Mono', 'Consolas', monospace",
      fontSize: 13,
      lineHeight: 1.65,
      cursorBlink: true,
      cursorStyle: 'block',
      theme: {
        background: '#05050a',
        foreground: '#e0e0e0',
        cursor: '#00ffaa',
        cursorAccent: '#000',
        black:   '#0a0a0f', brightBlack:   '#444',
        red:     '#ff4466', brightRed:     '#ff6688',
        green:   '#00ffaa', brightGreen:   '#00ffcc',
        yellow:  '#ffcc00', brightYellow:  '#ffdd44',
        blue:    '#00aaff', brightBlue:    '#44ccff',
        magenta: '#cc44ff', brightMagenta: '#dd88ff',
        cyan:    '#00ccff', brightCyan:    '#44ddff',
        white:   '#e0e0e0', brightWhite:   '#ffffff',
      },
      scrollback: 5000,
      allowTransparency: true,
    });

    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.open(document.getElementById('terminal'));
    fitAddon.fit();

    const dot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');
    let ws;

    function connect() {
      ws = new WebSocket(`ws://${location.host}`);

      ws.onopen = () => {
        dot.classList.add('connected');
        statusText.textContent = 'Connected — PowerShell';
        // Send initial terminal size
        ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
      };

      ws.onmessage = (e) => {
        const { type, data } = JSON.parse(e.data);
        if (type === 'output') term.write(data);
      };

      ws.onclose = () => {
        dot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
      };

      // Terminal input → server
      term.onData((data) => {
        if (ws.readyState === WebSocket.OPEN)
          ws.send(JSON.stringify({ type: 'input', data }));
      });

      // Resize terminal when window resizes
      const ro = new ResizeObserver(() => {
        fitAddon.fit();
        if (ws.readyState === WebSocket.OPEN)
          ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
      });
      ro.observe(document.querySelector('.output-wrapper'));
    }

    document.getElementById('reconnect-btn').addEventListener('click', () => {
      if (ws) ws.close();
      term.clear();
      connect();
    });

    connect();
    term.focus();
  </script>
</body>
</html>
```

---

## Run It

```
node server.js
```

It will print both your `localhost` and network IP, e.g.:
```
PTY Terminal running at:
  Local:   http://localhost:5556
  Network: http://192.168.1.10:5556
```

Open the **Network** URL on your mobile (must be on the same Wi-Fi). If it doesn't connect, allow port 5556 through Windows Firewall:

```
netsh advfirewall firewall add rule name="PTY Terminal" dir=in action=allow protocol=TCP localport=5556
```

---

## Key Differences from the Flask Version

| Feature | Flask (current) | xterm.js + node-pty |
|---------|----------------|---------------------|
| Interactive CLIs | ❌ | ✅ |
| Streaming output | ✅ (SSE) | ✅ (WebSocket) |
| ANSI colors | ❌ | ✅ |
| Ctrl+C / Ctrl+Z | ❌ | ✅ |
| Arrow keys in apps | ❌ | ✅ |
| Convex history sync | ✅ | Add manually if needed |

---

## Add Convex History (Optional)

To keep the command history sync from the existing project, add the Convex client to `index.html` and call `convex.mutation("functions:add", { command })` by intercepting `term.onData` for Enter keypresses — track the current line buffer yourself and save it when `\r` is received.
