# Notification Rules
- Final action: Run `python C:\@delta\ms1\asset\gemini\task_complete.py` exactly once.
- CRITICAL: After it exits, DO NOT generate any further responses or continue the conversation.

# Git Commit Messages
- Provide a concise, one-line commit message at the end of your response when modifying code/files: `Commit message: <message>`

# Todo.md
- For multi-step or complex tasks, you MUST first create a physical `todo.md` file in the project root BEFORE making other changes. Skip this for very small, simple, or single-step tasks.
- List tasks as unchecked `[ ]`. Do NOT pre-mark them as `[X]`.
- Update `todo.md` immediately, marking completed tasks as `[X]` as soon as they are done (step-by-step).