import os
import platform
import sys
import datetime
import json

def execute_tool(tool_name, arguments):
    """Executes a local tool and returns the result as a string."""
    try:
        if tool_name == "read_file":
            filepath = arguments.get('filepath')
            if not filepath:
                return "Error: filepath argument is required."
            if not os.path.exists(filepath):
                return f"Error: File not found: {filepath}"
            if os.path.isdir(filepath):
                return f"Error: {filepath} is a directory, not a file. Use list_directory instead."
            
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                # Cap the output at 8000 characters to prevent blowing up the AI context
                if len(content) > 8000:
                    return content[:8000] + "\n\n... (Content truncated because it is too large)"
                return content
                
        elif tool_name == "list_directory":
            path = arguments.get('path', '.')
            if not path:
                path = '.'
            if not os.path.exists(path):
                return f"Error: Directory not found: {path}"
            if not os.path.isdir(path):
                return f"Error: {path} is not a directory."
            
            files = os.listdir(path)
            if not files:
                return "Directory is empty."
            return "\n".join(files)
            
        elif tool_name == "get_system_info":
            info = [
                f"OS: {platform.system()} {platform.release()} ({platform.architecture()[0]})",
                f"Python: {sys.version}",
                f"Current Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Current Working Directory: {os.getcwd()}"
            ]
            return "\n".join(info)
            
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"
        
    return f"Unknown tool: {tool_name}"

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the contents of a local file. Use this to read code or config files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string", 
                        "description": "Absolute or relative path to the file to read."
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Lists the files and folders in a local directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string", 
                        "description": "Path to the directory, e.g. ./ or C:/path/to/folder"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Gets the current system OS, Python version, current working directory, and local time.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]
