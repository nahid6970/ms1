# Notification Rules
- When you have completely finished helping the user, run the notification script EXACTLY ONCE as your final action.
- Command: `python C:\@delta\ms1\asset\gemini\task_complete.py`
- The notification displays a professional-styled popup window with the message "Task Completed Successfully"
- CRITICAL: After running this script and it exits (when the user clicks Dismiss), DO NOT generate any further responses or continue the conversation.
- Run it for both complex tasks and simple conversations (hi, hello, thanks, etc.)
- This must be the absolute last action - no text, no explanations after running the command.

# Git Commit Messages
- Whenever you modify any code or files in the repository, you MUST provide a concise, one-line git commit message at the end of your response, just before calling the notification tool.
- This commit message should be clearly labeled (e.g., "Commit message: <message>").
- Do not provide a commit message if no files were modified or for general inquiries.

# Todo.md
- CRITICAL: whenever you are going to modify any code, add any feature etc, you MUST first create a physical `todo.md` file in the project root folder BEFORE making any other code changes. The file must exist on disk before editing other files. Do NOT use the built-in todo_list tool as a substitute.
- The `todo.md` should initially describe what you are asked to do and list all tasks starting as unchecked `[ ]`:
  - [] Task 1
  - [] Task 2
  - [] Task 3
- CRITICAL: Do NOT pre-mark tasks as `[X]` when creating the `todo.md`. All tasks must start as `[ ]`.
- CRITICAL: Whenever you finish any individual task, you MUST immediately update the physical `todo.md` file to mark that specific task as `[X]` (e.g. `- [X] Task 1`) before proceeding to subsequent tasks or modifying more code. The file must reflect real, step-by-step progress at all times, rather than marking everything at the end of the run. This is because if the AI agent fails mid-run, the user can continue from the exact state documented in the list.