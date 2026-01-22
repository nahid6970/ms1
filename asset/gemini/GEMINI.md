# Notification Rules
- When you have completely finished helping the user, call the notification tool EXACTLY ONCE as your final action.
- The notification displays a cyberpunk-styled popup window with the message "Your task has been Completed✅"
- Tool name: `show_task_complete_notification`
- CRITICAL: After calling this tool, DO NOT generate any further responses or continue the conversation. The tool's response will tell you to stop.
- Call it for both complex tasks and simple conversations (hi, hello, thanks, etc.)
- This must be the absolute last action - no text, no explanations after calling it.