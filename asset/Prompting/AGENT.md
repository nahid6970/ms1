# How to Read This File
- Each rule is tagged with either [ACTIVE] or [INACTIVE].
- [ACTIVE] — This rule is enforced. The AI agent MUST follow it at all times.
- [INACTIVE] — This rule is disabled. The AI agent MUST ignore it completely as if it doesn't exist.
- To enable or disable a rule, change its tag between [ACTIVE] and [INACTIVE].

# Notification Rules [ACTIVE]
- When you have completely finished helping the user, run `python C:\@delta\ms1\asset\Prompting\update_notification.py` EXACTLY ONCE as your final action.
- This triggers a desktop notification popup via the daemon running in the background.
- Do this for both complex tasks and simple conversations (hi, hello, thanks, etc.)

# Running Commands [ACTIVE]
- CRITICAL: Do not run any command to download or build any packages — give me all the commands and I will run them myself.
- When adding new features, prioritize existing libraries or tools. Use `uv add <package_name>` to manage dependencies instead of writing custom code for functionality that is already available. Import and configure existing tools to keep the codebase clean and maintainable. If there is no way to implement the features with existing tools then add more code to implement the features.

# Adding .gitignore file [ACTIVE]
- Add a .gitignore file for newly created projects with items that are unnecessary to commit.

# Android Projects [ACTIVE]
- For Android projects I have android-cli installed, so you can utilize it to build, run, etc.

# AI WORKFLOW STYLE
## Suggestion Style — Proactive Approaches [INACTIVE]
- Before implementing a solution, offer 2–3 different approaches or ideas (including unconventional ones) and let the user choose.

## Suggestion Style — Open to Creative Ideas [INACTIVE]
- Be open to unconventional, experimental, or "wakey" ideas. When the user seems to be exploring, suggest surprising or creative alternatives they may not have considered.

## Suggestion Style — Suggestion-First Workflow [ACTIVE]
- For any new feature or design decision, first present a short list of suggestions or options before proceeding. Don't assume the obvious path is the preferred one.

## Suggestion Style — Combination [INACTIVE]
- When faced with a task that has multiple valid approaches — especially open-ended or creative ones — pause and offer 2–3 suggestions (including at least one unconventional idea) before diving in. Let the user pick or say "just go for it."

# Preview / Smoketest [ACTIVE]
- When the user says "give me a preview", "smoketest", "show me how it looks", or similar — generate a self-contained HTML file that visually demonstrates all the suggestions or options being discussed.
- The HTML must be fully animated and styled (CSS animations, gradients, etc.) so it accurately represents what the final implementation will look, feel, and animate like.
- Save the file to the current project directory and immediately open it in the browser with `start <path>`.
- Each option must be clearly labelled (e.g. "Option A — Glassmorphism") so the user can compare and pick one.