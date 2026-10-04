# Notification Rules

<!-- OPTION A: Direct run — model runs the script as a command -->
- When you have completely finished helping the user, run the notification script EXACTLY ONCE as your final action.
- Command: `python C:\@delta\ms1\asset\Prompting\notify_run.py`
- The notification displays a styled popup window with the message "Task Completed Successfully".
- Run it for both complex tasks and simple conversations (hi, hello, thanks, etc.)
- This must be the absolute last action — no text or explanations after running the command.

<!-- OPTION B: Daemon style — model writes datetime to file, daemon shows popup -->
<!-- Uncomment below and comment out OPTION A to switch
- When you have completely finished helping the user, write the current date and time (format: YYYY-MM-DD HH:MM) to `C:\Users\nahid\notification.txt` EXACTLY ONCE as your final action.
- This triggers a desktop notification popup via the daemon running in the background.
- Do this for both complex tasks and simple conversations (hi, hello, thanks, etc.)
- This must be the absolute last action.
-->

# Running Commands
- CRITICAL: Do not run any command to download or build any packages — give me all the commands and I will run them myself.
- When adding new features, prioritize existing libraries or tools. Use `uv add <package_name>` to manage dependencies instead of writing custom code for functionality that is already available. Import and configure existing tools to keep the codebase clean and maintainable. If there is no way to implement the features with existing tools then add more code to implement the features.

# Git Commit Messages
- CRITICAL: Whenever you modify any code or files, you MUST output a git commit message at the very end of your response, formatted exactly as: `Commit message: <message>`. This is mandatory.
- Do not provide a commit message if no files were modified or for general inquiries.

# Adding .gitignore file
- Add a .gitignore file for newly created projects with items that are unnecessary to commit.

# Android Projects
- For Android projects I have android-cli installed, so you can utilize it to build, run, etc.
