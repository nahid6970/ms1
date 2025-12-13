# Gemini CLI Dashboard - Tips & Troubleshooting

## Working Directory
All Gemini CLI commands run from: `C:\Users\nahid\ms\ms1\Testing\geminiTesting`

Any files created by Gemini will be saved there.

## YOLO Mode Enabled!

The dashboard now runs Gemini CLI with `--yolo` mode, which means:
- ✅ File system tools ARE available (write_file, read_file, etc.)
- ✅ Tools are auto-approved without confirmation
- ✅ Gemini can create, edit, and manage files directly
- ✅ All files are created in: `C:\Users\nahid\ms\ms1\Testing\geminiTesting`

## How It Works Now

You can ask Gemini to:
- "Create a Python script to add 2+2" ✅ (will create the file)
- "Make a file called test.py with hello world" ✅ (will create it)
- "Read the contents of config.json" ✅ (if file exists)
- "List all Python files" ✅ (will list them)

All file operations happen in the working directory automatically!

## Best Practices

1. **Ask for code output, not file creation:**
   - "Show me Python code to add numbers"
   - "Generate a function that does X"

2. **Be direct:**
   - "Calculate 2+2"
   - "Explain how to use Flask"

3. **Copy code manually:**
   - Get the code from Gemini
   - Save it yourself in the working directory

## Example Prompts That Work Well

- "Write a Python function to calculate factorial"
- "Explain how async/await works in JavaScript"
- "Generate HTML for a login form"
- "Debug this code: [paste code]"
- "What's the difference between let and const?"

## Example Prompts That May Cause Issues

- "Create a file called test.py with code to add numbers"
- "Read the contents of config.json"
- "List all Python files in the directory"

These require file system access which the CLI doesn't have.
