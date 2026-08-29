# FCC Claude + Gemini Troubleshooting

This documents the issue where `fcc-claude` starts, but requests fail with a timeout or `Connection refused`.

## What happened

There were two separate problems:

1. `fcc-claude` was started before `fcc-server` had finished starting. FCC performs a short readiness check, while the server may still be discovering Gemini models. This produced:

   ```text
   Free Claude Code proxy is not reachable at http://127.0.0.1:8082: timed out
   ```

2. Claude Code still had old Claude Code Router settings in `%USERPROFILE%\.claude\settings.json`:

   - `apiKeyHelper`
   - `ANTHROPIC_BASE_URL=http://127.0.0.1:3456`
   - `ANTHROPIC_API_BASE_URL=http://127.0.0.1:3456`
   - `CLAUDE_AGENT_API_BASE_URL=http://127.0.0.1:3456`

   FCC uses port `8082`, but the old Router used port `3456`. Because nothing was listening on port `3456`, Claude displayed:

   ```text
   Connection refused
   ```

The `Haiku 4.5` label in Claude Code is only the Claude model alias. FCC routes the request according to `%USERPROFILE%\.fcc\.env`, which is configured to use Gemini.

## Normal startup

Open two PowerShell terminals.

Terminal 1:

```powershell
fcc-server
```

Wait until the server reports `Application startup complete`. Then use Terminal 2:

```powershell
Invoke-RestMethod http://127.0.0.1:8082/health
fcc-claude
```

The health command should return:

```text
status
------
healthy
```

## If FCC reports a timeout

Check whether the server is listening:

```powershell
Get-NetTCPConnection -LocalPort 8082 -ErrorAction SilentlyContinue
```

If there is no `Listen` entry, start `fcc-server` and wait for startup to finish before running `fcc-claude`.

If the server is listening, verify the health endpoint directly:

```powershell
Invoke-RestMethod http://127.0.0.1:8082/health
```

## If Claude shows `Connection refused`

Check both ports:

```powershell
Test-NetConnection 127.0.0.1 -Port 8082 -InformationLevel Quiet
Test-NetConnection 127.0.0.1 -Port 3456 -InformationLevel Quiet
```

For FCC, port `8082` should be `True`. Port `3456` is only needed when intentionally using Claude Code Router.

Open the Claude settings file:

```powershell
notepad "$env:USERPROFILE\.claude\settings.json"
```

When using FCC, remove the complete `apiKeyHelper` property and these old Router environment properties:

```json
"ANTHROPIC_BASE_URL": "http://127.0.0.1:3456",
"ANTHROPIC_API_BASE_URL": "http://127.0.0.1:3456",
"CLAUDE_AGENT_API_BASE_URL": "http://127.0.0.1:3456"
```

Keep the JSON valid. A safe FCC-compatible settings file can contain:

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY": "1"
  },
  "theme": "dark",
  "model": "haiku"
}
```

Exit any existing Claude session after changing the file, then start a new one:

```powershell
fcc-claude
```

## Authentication warning

This warning means Claude sees both `ANTHROPIC_AUTH_TOKEN` and `apiKeyHelper`:

```text
Both ANTHROPIC_AUTH_TOKEN and apiKeyHelper set
```

FCC intentionally supplies `ANTHROPIC_AUTH_TOKEN` to authenticate with its local proxy. Remove `apiKeyHelper` from the Claude settings when using FCC. Do not remove the FCC token from `%USERPROFILE%\.fcc\.env` unless changing the FCC server authentication configuration.

## If port 8082 is already occupied

Find the process using it:

```powershell
Get-NetTCPConnection -LocalPort 8082 -State Listen |
  Select-Object LocalAddress,LocalPort,OwningProcess
```

Inspect the process before taking action:

```powershell
Get-Process -Id <PID>
```

Do not terminate a process unless you know it is the stale FCC server or another application you intentionally want to stop. Normally, reuse the already-running healthy FCC server instead of starting another one.

## Useful locations

- Claude settings: `%USERPROFILE%\.claude\settings.json`
- FCC configuration: `%USERPROFILE%\.fcc\.env`
- FCC server log: `%USERPROFILE%\.fcc\logs\server.log`
- FCC server URL: `http://127.0.0.1:8082`
- FCC health check: `http://127.0.0.1:8082/health`

The PowerShell update notification is unrelated to FCC or Gemini connectivity.

## Selecting Gemini models from `/model`

FCC advertises discovered Gemini models in Claude Code's `/model` menu. If you select an exact entry such as:

```text
gemini/models/gemini-3.5-flash-lite
```

FCC routes that session to Gemini 3.5. It does not fall back to the configured Gemini 3.1 model.

The selection controls are:

- Press `s` to use the selected model for the current session only.
- Press `Enter` to make the selected model the default for new sessions.
- Select `Default` to use the server's configured `MODEL` value.

With this configuration:

```text
MODEL=gemini/models/gemini-3.1-flash-lite
MODEL_OPUS=
MODEL_SONNET=
MODEL_HAIKU=
```

the `Default` option uses Gemini 3.1. Claude compatibility aliases such as `Opus`, `Sonnet`, `Haiku`, and `Claude Fable 5` also fall back to Gemini 3.1 because their per-alias settings are empty. They are not Anthropic API calls; FCC translates Claude Code requests to the configured Gemini provider.

The `no thinking` variant points to the same Gemini model but requests it without thinking/reasoning output.
