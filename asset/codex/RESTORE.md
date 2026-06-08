# Codex Restore Guide

Copy these files after a PC reset:

1. `C:\@delta\ms1\asset\codex\task_complete.ps1`
   - Restore to the same path.

2. `C:\@delta\ms1\asset\codex\codex_config.toml`
   - Copy to `C:\Users\nahid\.codex\config.toml`

3. `C:\@delta\ms1\asset\codex\codex_hooks.json`
   - Copy to `C:\Users\nahid\.codex\hooks.json`

After restoring:

1. Start Codex once.
2. If the hook is marked untrusted, open `/hooks` and trust it.
3. Restart Codex if needed.
