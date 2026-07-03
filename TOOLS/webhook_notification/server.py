"""
server.py — Self-hosted webhook notification server.

Receives HTTP POST requests and shows a cyberpunk desktop popup.

Endpoints:
    POST /notify          - JSON body: {title, message, source, token}
    POST /webhook         - alias for /notify
    GET  /                - health check
    GET  /status          - server info

Security:
    Set AUTH_TOKEN in config.json (or env var WEBHOOK_TOKEN).
    Leave blank to disable token check (LAN-only use).

Run:
    python server.py
    python server.py --port 5050 --host 0.0.0.0
"""

import os
import sys
import json
import argparse
import subprocess
import threading
import logging
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"

DEFAULT_CONFIG = {
    "host": "0.0.0.0",
    "port": 5050,
    "auth_token": "",          # empty = no auth required (good for Tailscale-only)
    "log_notifications": True,
    "default_title": "Webhook Notification",
    "default_source": "webhook"
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        # Fill in any missing keys from defaults
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        return cfg
    # Write defaults on first run
    with open(CONFIG_FILE, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    print(f"[server] Created config.json with defaults. Edit it to set a token.")
    return DEFAULT_CONFIG.copy()


config = load_config()

# Token can also be overridden by env var
AUTH_TOKEN = os.environ.get("WEBHOOK_TOKEN", config["auth_token"])

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE = BASE_DIR / "notifications.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ]
)
log = logging.getLogger("webhook")

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

NOTIFY_SCRIPT = BASE_DIR / "notify.py"
PYTHON_EXE    = sys.executable   # same python that's running the server


def _launch_popup(title: str, message: str, source: str):
    """Spawn the notification popup in a separate process (non-blocking)."""
    try:
        subprocess.Popen(
            [PYTHON_EXE, str(NOTIFY_SCRIPT), title, message, source],
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
    except Exception as e:
        log.error(f"Failed to launch popup: {e}")


def _check_token(req) -> bool:
    """Return True if auth passes (or no token configured)."""
    if not AUTH_TOKEN:
        return True
    # Accept token from JSON body, query param, or Authorization header
    data  = req.get_json(silent=True) or {}
    token = (
        data.get("token")
        or req.args.get("token")
        or req.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    )
    return token == AUTH_TOKEN


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "webhook-notification-server",
        "time": datetime.now().isoformat()
    })


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "running",
        "port": config["port"],
        "auth_required": bool(AUTH_TOKEN),
        "log_file": str(LOG_FILE),
    })


def _handle_notify():
    """Shared handler for /notify and /webhook."""
    if not _check_token(request):
        log.warning(f"Unauthorized request from {request.remote_addr}")
        return jsonify({"error": "Unauthorized"}), 401

    # Accept JSON or plain-text body
    data = request.get_json(silent=True) or {}

    if not data and request.data:
        # Plain text body → use as message
        data = {"message": request.data.decode("utf-8", errors="replace")}

    title   = str(data.get("title",   config["default_title"])).strip()
    message = str(data.get("message", "")).strip()
    source  = str(data.get("source",  config["default_source"])).strip()

    if not message:
        return jsonify({"error": "message is required"}), 400

    log.info(f"[{source}] {title}: {message[:80]}")

    # Launch popup in a background thread so HTTP response returns immediately
    threading.Thread(
        target=_launch_popup,
        args=(title, message, source),
        daemon=True
    ).start()

    return jsonify({
        "status": "sent",
        "title": title,
        "message": message,
        "source": source,
    })


@app.route("/notify",  methods=["POST"])
def notify():
    return _handle_notify()


@app.route("/webhook", methods=["POST"])
def webhook():
    return _handle_notify()


# Also accept GET /notify?message=...&title=...&token=...
# Useful for browser address-bar testing or simple web links
@app.route("/notify", methods=["GET"])
def notify_get():
    if not _check_token(request):
        return jsonify({"error": "Unauthorized"}), 401

    title   = request.args.get("title",   config["default_title"])
    message = request.args.get("message", "")
    source  = request.args.get("source",  "browser")

    if not message:
        return jsonify({"error": "message param required"}), 400

    log.info(f"[{source}] {title}: {message[:80]}")
    threading.Thread(
        target=_launch_popup,
        args=(title, message, source),
        daemon=True
    ).start()
    return jsonify({"status": "sent"})


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Webhook notification server")
    parser.add_argument("--host", default=config["host"],
                        help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=config["port"],
                        help="Port number (default: 5050)")
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════╗")
    print("║   WEBHOOK NOTIFICATION SERVER  ◈  RUNNING   ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  Address : http://{args.host}:{args.port:<26}║")
    print(f"║  Auth    : {'YES — token required' if AUTH_TOKEN else 'NO  — open (LAN-safe)':<27}║")
    print(f"║  Log     : {str(LOG_FILE)[:39]:<40}  ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    print("  Endpoints:")
    print(f"    POST http://<your-ip>:{args.port}/notify")
    print(f"    POST http://<your-ip>:{args.port}/webhook")
    print()

    app.run(host=args.host, port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
