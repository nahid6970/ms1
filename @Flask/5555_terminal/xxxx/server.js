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
