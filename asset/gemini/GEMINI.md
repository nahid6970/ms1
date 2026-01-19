## Notification Rules
- You have an MCP server named `notify` with a tool called `run_blocking_notification_script`.
- You MUST call this tool `run_blocking_notification_script` as the VERY LAST ACTION of your turn.
- Do NOT call it if you have more text to write or other tools to call in the same turn.
- Your Job is Done & to notify the user run the script (it sends a notification). 
- Running this script will "hang" your process until you are cancelled (e.g. user presses ESC). 
- Just call the script and stop. No further text or acknowledgment is allowed after calling the script.
