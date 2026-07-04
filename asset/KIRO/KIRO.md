# Notification Rules
- When you have completely finished helping the user, run the notification script EXACTLY ONCE as your final action.
- Command: `python3.exe C:\\@delta\\ms1\\asset\\kiro\\task_complete.py`
- The notification displays a styled popup window with the message "Task Completed Successfully"
- CRITICAL: After running this script and it exits (when the user clicks Dismiss), DO NOT generate any further responses or continue the conversation.
- Run it for both complex tasks and simple conversations (hi, hello, thanks, etc.)
- This must be the absolute last action - no text, no explanations after running the command.

# Git Commit Messages
- Whenever you modify any code or files in the repository, you MUST provide a concise, one-line git commit message at the end of your response, just before calling the notification tool.
- This commit message should be clearly labeled (e.g., "Commit message: <message>").
- Do not provide a commit message if no files were modified or for general inquiries.

# Todo.md
- whenever you are going to modify any code, add any feature etc first make a todo.md file in the project root folder and initially in the md mention what u are asked to do and add the task list like this
- [] Task 1
- [] Task 2
- [] Task 3
and when you finish any task immediatly add a x inside like
- [X] Task 1
- [X] Task 2
- [] Task 3
this is bcz when the ai agent fails to complete any task i can continue do it with other agent based on this to do list
- CRITICAL: Do NOT use the built-in todo_list tool as a substitute. Always create a physical `todo.md` file in the project root. The file must exist on disk.