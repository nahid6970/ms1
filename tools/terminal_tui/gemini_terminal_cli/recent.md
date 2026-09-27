1. Project DNA (Permanent): Python-based Windows terminal Gemini CLI with an interactive prompt/TUI, local tools, encrypted API-account storage, and persistent preferences. Its primary goal is practical terminal chat and coding assistance with resilient Gemini access.

2. Latest Implementation:
- PC remote command connection: prefer SSH from another device using `ssh -p 22 nahid@192.168.0.101`. Requests phrased as “7777 and run ...” are sent over SSH; without a directory, SSH starts in the PC user's home folder. Keep the password out of project files and chat; use terminal password prompting or configure SSH keys for unattended access. Flask `/lan` remains the PC file browsing/editing route.
- `gemini_cli.py`: Added loopback proxy using encrypted `api_accounts.lock`, quota/rate-limit failover, JSON/SSE forwarding, explicit stream close, safe account/model-prefixed diagnostics, and `/test` synchronization into Pi's failover catalog.
- `README.md`: Documents proxy, model synchronization, and safe logging.
- `C:\Users\nahid\.pi\agent\auth.json`, `models.json`, `settings.json`: Configured failover-only Pi provider, enabled models, and default `google-failover/gemini-3.1-flash-lite`.

3. Critical Context: Start the proxy with `--proxy-key pi-local-secret --password 182358`; the first value is Pi-to-proxy authentication, while the second unlocks real keys in `api_accounts.lock`. Bind to `127.0.0.1`. Pi defaults to `google-failover/gemini-3.1-flash-lite`; restart the proxy after source changes. `/test` syncs passing models, then Pi needs `/reload`. The router stays on a successful account and switches only on retryable failures.

4. Pending Task: Confirm a quota/503 event produces visible `attempt`, `upstream_error`, `failover`, and `success` log entries across two accounts.
