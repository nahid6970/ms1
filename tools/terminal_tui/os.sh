#!/data/data/com.termux/files/usr/bin/bash
# Launch Terminal TUI directly in Termux on Android.

set -euo pipefail

if [[ -z "${PREFIX:-}" || ! "$PREFIX" == *com.termux* ]]; then
    echo "Run this script from Termux on Android." >&2
    echo "Install Python first with: pkg install python" >&2
    exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v python >/dev/null 2>&1; then
    echo "Python is missing. Install it with: pkg install python" >&2
    exit 1
fi

PORT=5577
LAN_IP="$(ip route get 1.1.1.1 2>/dev/null | awk '{for (i=1;i<=NF;i++) if ($i=="src") {print $(i+1); exit}}' || true)"

echo "Starting Terminal TUI in Termux..."
echo "On this phone, open: http://127.0.0.1:$PORT/"
if [[ -n "$LAN_IP" ]]; then
    echo "From another device on the same Wi-Fi, open: http://$LAN_IP:$PORT/"
fi
echo "Press Ctrl+C to stop."
exec python app.py
