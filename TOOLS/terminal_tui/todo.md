# Tasks
- [x] Replace old custom system prompt details textarea with a new dropdown select, a plus (+) button, and a settings/edit button in `#ai-copilot-popover`
- [x] Create `#ai-system-prompt-modal` dialog layout in HTML for adding, viewing, editing, and deleting multiple prompts
- [x] Implement javascript CRUD operations (`getCustomSystemPrompts`, `saveCustomSystemPrompts`, `saveCustomPrompt`, `deleteCustomPrompt`)
- [x] Implement migration function `migrateOldSystemPrompt()` to preserve user's existing system prompt as a default entry named "Saved Prompt"
- [x] Update submit query functions to dynamically inject the selected system prompt text
- [x] Test and push updates to github
