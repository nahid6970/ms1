# Claude Code Router + Gemini Setup

This guide is for setting up `Claude Code Router` with a `Gemini API key` on Windows while keeping `Codex CLI` separate.

## What to install first

Install in this order:

1. `Node.js` LTS
2. `Claude Code Router`
3. `Claude Code` if you want to use it through CCR
4. `Codex CLI` only if you want the OpenAI Codex client separately

## What each tool does

- `Claude Code Router` is the local router that manages providers and models.
- `Claude Code` is the agent client that can be pointed at CCR.
- `Codex CLI` is a separate OpenAI tool and does not need to use CCR.

## Install commands

Run these yourself in PowerShell:

```powershell
npm install -g @musistudio/claude-code-router
```

If you need Claude Code too, install it separately using the official method you normally use.

If you use Codex CLI separately, keep its configuration in `~/.codex/config.toml` and do not point it at CCR unless you explicitly want that.

## Start CCR

Open the CCR UI:

```powershell
ccr ui
```

If the command is not found, reopen the terminal after the global install.

## Where to put the Gemini API key

Put the Gemini API key inside `Claude Code Router`, not in Codex CLI.

Use one of these:

- CCR UI: `Providers` -> `Add Provider` -> Gemini provider -> paste the API key there
- CCR config storage:
  - Legacy/manual config: `%APPDATA%\claude-code-router\config.json`
  - Current runtime storage on newer versions: `%APPDATA%\claude-code-router\config.sqlite`

If you are using the UI, that is the safest place to enter the key.

## Recommended CCR provider settings for Gemini

Use the Gemini provider with:

- Provider name: `gemini`
- Base URL: `https://generativelanguage.googleapis.com/v1beta/models/`
- Models: for example `gemini-2.5-pro` or `gemini-2.5-flash`

If the UI offers a transformer or protocol choice, use the Gemini/native option for Gemini rather than an OpenAI-style wrapper unless you specifically know you need the wrapper.

## CCR commands you will use most often

### UI

```powershell
ccr ui
```

### Start the router

```powershell
ccr start
```

### Restart the router

```powershell
ccr restart
```

### Stop the router

```powershell
ccr stop
```

### Check version

```powershell
ccr --version
```

### Show help

```powershell
ccr --help
```

## How to use CCR without interfering with Codex CLI

Follow these rules:

- Do not set CCR-specific environment variables globally in PowerShell profile files.
- Do not put Gemini variables into Codex CLI config files.
- Keep CCR running only when you want to use Claude Code through CCR.
- Keep Codex CLI in its normal terminal session and normal config.
- If you want to be extra safe, use a separate terminal window for CCR and another one for Codex.

## Suggested workflow

1. Install `Node.js`.
2. Install `Claude Code Router`.
3. Launch `ccr ui`.
4. Add the Gemini provider and paste your API key there.
5. Start CCR from the UI or with `ccr start`.
6. Configure Claude Code to use CCR if needed.
7. Leave Codex CLI untouched unless you intentionally want to route it through CCR.

## Notes

- CCR listens on local ports by default, so it should not affect Codex CLI unless you explicitly connect Codex to it.
- If something looks wrong, check the CCR logs in the UI first.
- If you later want a separate config for Codex, keep it isolated from CCR.
