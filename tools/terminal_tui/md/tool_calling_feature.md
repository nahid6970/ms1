# AI Tool Calling (Function Calling) Implementation Plan

This document outlines how to add **Tool Calling** (also known as Function Calling) to the terminal UI so the AI can execute local actions (like reading files, searching the web, or running shell commands).

## 1. Overview of the Flow

1. **Define Tools:** The Python backend (`app.py`) defines a list of available tools in a standard JSON Schema format.
2. **Send Prompt + Tools:** When the user sends a message, the backend passes both the conversation history and the tool schema to the AI Provider (Gemini, Groq, OpenRouter).
3. **AI Decides:** 
   - If the AI can answer directly, it returns standard text.
   - If it needs information (e.g., "read app.py"), it returns a **Tool Call** object specifying the tool name and arguments.
4. **Backend Executes:** Python intercepts the Tool Call, runs the requested local function, and gets the result (e.g., the file content).
5. **Send Result to AI:** Python appends the tool's result to the conversation history and sends it back to the AI.
6. **Final Answer:** The AI reads the result and generates a final response for the user.

## 2. Recommended Tools to Implement First

*   `read_file(filepath)`: Allows the AI to read code or config files.
*   `list_directory(path)`: Helps the AI navigate the workspace.
*   `run_shell_command(command)`: Allows the AI to run builds, tests, or git commands (with user confirmation!).
*   `web_search(query)`: Allows the AI to look up latest documentation.

## 3. Example JSON Schema (OpenAI/Groq Format)

```json
{
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "Reads the contents of a local file.",
    "parameters": {
      "type": "object",
      "properties": {
        "filepath": {
          "type": "string",
          "description": "The absolute or relative path to the file."
        }
      },
      "required": ["filepath"]
    }
  }
}
```

## 4. Implementation Steps in `app.py`

1. **Create a Tool Execution Router:** A Python dictionary mapping tool names to actual Python functions.
    ```python
    def execute_tool(tool_name, arguments):
        if tool_name == "read_file":
            with open(arguments['filepath'], 'r') as f:
                return f.read()
        # ...
    ```
2. **Modify the Chat Endpoint (`/api/ai-chat`):**
    - Attach the `tools` array to the payload sent to Groq/OpenRouter/Gemini.
    - Check the response. If `response.choices[0].message.tool_calls` exists:
        - Extract the tool calls.
        - Loop through them, execute the python functions.
        - Append a message with `role: "tool"` (or `function`) containing the result.
        - Ping the AI API a second time with the updated history.
3. **UI Updates (Optional but Recommended):**
    - When the backend is executing a tool, send a temporary status to the frontend (e.g., "⚙️ AI is reading app.py...").

## 5. Security Considerations

- **Sandboxing:** Do not allow the AI to run destructive commands automatically. If implementing `run_shell_command`, the backend should pause and prompt the user in the UI to click "Approve" before actually running the command.
- **Path Traversal:** Ensure `read_file` validates paths so the AI cannot read sensitive files outside of the workspace directory.
