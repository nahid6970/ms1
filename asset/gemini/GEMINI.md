# Notification Rules
- When you have completely finished helping the user, call the notification tool EXACTLY ONCE as your final action.
- The notification displays a professional-styled popup window with the message "Task Completed Successfully"
- Tool name: `show_task_complete_notification`
- CRITICAL: After calling this tool, DO NOT generate any further responses or continue the conversation. The tool's response will tell you to stop.
- Call it for both complex tasks and simple conversations (hi, hello, thanks, etc.)
- This must be the absolute last action - no text, no explanations after calling it.

# Git Commit Messages
- Whenever you modify any code or files in the repository, you MUST provide a concise, one-line git commit message at the end of your response, just before calling the notification tool.
- This commit message should be clearly labeled (e.g., "Commit message: <message>").
- Do not provide a commit message if no files were modified or for general inquiries.