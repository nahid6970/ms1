#!/usr/bin/env bash
# Start the Windows-hosted Terminal TUI so it can be opened from Android.
# Run this from Git Bash in the project directory: bash os.sh

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
APP_FILE="$SCRIPT_DIR/app.py"
PORT=5577

if [[ ! -f "$APP_FILE" ]]; then
    echo "Could not find app.py beside os.sh: $APP_FILE" >&2
    exit 1
fi

# This app's interactive terminal backend requires Windows. On Windows, run it
# here and let Android connect through the PC's local network address.
if [[ "${OS:-}" != "Windows_NT" ]]; then
    echo "This app needs to run on its Windows host (its terminal backend uses Windows)." >&2
    echo "Run 'bash os.sh' from Git Bash on the Windows PC, then open the printed URL on Android." >&2
    exit 1
fi

PYTHON="$(command -v python || command -v py || true)"
if [[ -z "$PYTHON" ]]; then
    echo "Python was not found. Install Python 3.12+ and try again." >&2
    exit 1
fi

LAN_IP="$(powershell.exe -NoProfile -Command "(Get-NetIPConfiguration | Where-Object { \$_.IPv4DefaultGateway } | Select-Object -First 1 -ExpandProperty IPv4Address).IPAddress" 2>/dev/null | tr -d '\r' || true)"

echo "Starting Terminal TUI on port $PORT..."
echo "On Android connected to the same Wi-Fi, open: http://${LAN_IP:-<PC-LAN-IP>}:$PORT/"
echo "If it does not connect, allow Python through Windows Defender Firewall on Private networks."
echo "Press Ctrl+C here to stop the app."
cd "$SCRIPT_DIR"
exec "$PYTHON" app.py
