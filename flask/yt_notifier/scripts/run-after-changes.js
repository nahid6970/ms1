#!/usr/bin/env node

const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const root = process.cwd();
const debounceMs = Number(process.env.WATCH_DEBOUNCE_MS || 1200);
const watchPaths = splitEnv("WATCH_PATHS", ["convex", "public", "package.json", "wrangler.toml"]);
const startCommands = splitEnv("WATCH_START", ["npx convex dev"]);
const runCommands = splitEnv("WATCH_RUN", ["npm run deploy:pages"]);

let timer = null;
let running = false;
let pending = false;

function splitEnv(name, fallback) {
  if (!Object.prototype.hasOwnProperty.call(process.env, name)) return fallback;
  const value = process.env[name].trim();
  if (!value) return [];
  return value
    .split("&&")
    .map((command) => command.trim())
    .filter(Boolean);
}

function log(message) {
  console.log(`[watch] ${message}`);
}

function runCommand(command, mode = "inherit") {
  return new Promise((resolve) => {
    log(`running: ${command}`);
    const child = spawn(command, {
      cwd: root,
      env: process.env,
      shell: true,
      stdio: mode,
      windowsHide: false,
    });

    child.on("close", (code) => {
      if (code === 0) log(`finished: ${command}`);
      else log(`failed (${code}): ${command}`);
      resolve(code || 0);
    });
  });
}

function startCommand(command) {
  log(`starting: ${command}`);
  const child = spawn(command, {
    cwd: root,
    env: process.env,
    shell: true,
    stdio: "inherit",
    windowsHide: false,
  });

  child.on("exit", (code, signal) => {
    log(`stopped: ${command} (${signal || code})`);
  });
}

async function runAfterChange() {
  if (running) {
    pending = true;
    return;
  }

  running = true;
  do {
    pending = false;
    for (const command of runCommands) {
      const code = await runCommand(command);
      if (code !== 0) break;
    }
  } while (pending);
  running = false;
}

function schedule(filePath) {
  if (timer) clearTimeout(timer);
  log(`change detected: ${filePath || "unknown"}`);
  timer = setTimeout(runAfterChange, debounceMs);
}

function watchTarget(target) {
  const absolute = path.resolve(root, target);
  if (!fs.existsSync(absolute)) {
    log(`skipping missing path: ${target}`);
    return;
  }

  const stat = fs.statSync(absolute);
  fs.watch(
    absolute,
    { recursive: stat.isDirectory() },
    (_event, filename) => schedule(filename ? path.join(target, filename) : target),
  );
  log(`watching: ${target}`);
}

for (const command of startCommands) startCommand(command);
for (const target of watchPaths) watchTarget(target);

if (runCommands.length === 0) {
  log("WATCH_RUN is empty; no after-change commands will run.");
} else {
  log(`after-change commands: ${runCommands.join(" && ")}`);
}

process.stdin.resume();
