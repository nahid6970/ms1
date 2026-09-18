# Gemini Failover Setup

This setup connects Pi to the local Gemini failover proxy provided by:

`C:\@delta\ms1\tools\terminal_tui\gemini_terminal_cli\gemini_cli.py`

## Files required in this folder

### `auth.json`

Contains Pi's local proxy credential:

```json
"google-failover": {
  "type": "api_key",
  "key": "pi-local-secret"
}
```

The existing direct `google` credential can remain unchanged.

### `models.json`

Defines the `google-failover` provider and points it to:

`http://127.0.0.1:8765/v1beta`

It exposes `google-failover/gemini-3.5-flash` to Pi.

### `settings.json`

The enabled-model list must contain:

`google-failover/gemini-3.5-flash`

Otherwise the provider can exist but remain hidden from Pi's model picker.

## Start command

Run this in a separate PowerShell window:

```powershell
python C:\@delta\ms1\tools\terminal_tui\gemini_terminal_cli\gemini_cli.py --proxy --proxy-port 8765 --proxy-key pi-local-secret --password 182358
```

The proxy password unlocks the real Gemini accounts stored in the CLI's encrypted `api_accounts.lock`. Pi only sends `pi-local-secret` to the local proxy; it never receives the real Google keys or the account-store password.

## Do not edit for this setup

`models-store.json`, `provider-failover.json`, and `provider-failover-state.json` are not required for this local Gemini proxy route. After changing provider files, restart Pi or run `/reload`, then select `google-failover/gemini-3.5-flash`.
