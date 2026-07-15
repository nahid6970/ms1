import os
import platform
import sys
import datetime
import json
import requests

def execute_tool(tool_name, arguments, tavily_api_key=None):
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

        elif tool_name == "write_file":
            filepath = arguments.get('filepath')
            content = arguments.get('content', '')
            if not filepath:
                return "Error: filepath argument is required."
            
            # Create directory if it doesn't exist
            dirname = os.path.dirname(filepath)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to {filepath}."

        elif tool_name == "delete_file":
            filepath = arguments.get('filepath')
            if not filepath:
                return "Error: filepath argument is required."
            if not os.path.exists(filepath):
                return f"Error: File not found: {filepath}"
            
            if os.path.isdir(filepath):
                import shutil
                shutil.rmtree(filepath)
                return f"Successfully deleted directory and its contents: {filepath}"
            else:
                os.remove(filepath)
                return f"Successfully deleted file: {filepath}"
                
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

        elif tool_name == "web_search":
            query = arguments.get('query')
            if not query:
                return "Error: query argument is required."
            if not tavily_api_key:
                return "Error: Tavily API Key is not configured. Please set it in AI Tools Config (🛠️)."
            
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": 5
            }
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code != 200:
                return f"Error from Tavily API (HTTP {res.status_code}): {res.text}"
            
            data = res.json()
            results = data.get('results', [])
            if not results:
                return "No search results found."
            
            formatted = []
            for r in results:
                formatted.append(f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n")
            return "\n".join(formatted)

        elif tool_name == "run_shell_command":
            command = arguments.get('command')
            if not command:
                return "Error: command argument is required."
            
            import subprocess
            try:
                # Runs command in system shell (e.g. cmd.exe on Windows, bash on Unix)
                res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
                out = res.stdout or ""
                err = res.stderr or ""
                
                combined = ""
                if out:
                    combined += out
                if err:
                    if combined:
                        combined += "\n"
                    combined += f"Stderr:\n{err}"
                
                if not combined.strip():
                    return f"Command completed with exit code {res.returncode} (No output)."
                
                if len(combined) > 8000:
                    return combined[:8000] + "\n\n... (Output truncated because it is too large)"
                return combined
            except subprocess.TimeoutExpired:
                return "Error: Command execution timed out after 15 seconds."
            
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
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the web for real-time information, latest documentation, or troubleshooting guides.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query, e.g., 'Python flask socketio emit to specific client'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Creates a new file or overwrites an existing one with the provided content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file to write."},
                    "content": {"type": "string", "description": "The full text content to write into the file."}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Deletes a file or directory from the local file system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file or directory to remove."}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Executes a shell command on the host machine and returns stdout/stderr. Use to run compile, build, test, or lookup commands.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute, e.g. 'dir', 'git status', 'python test.py'"
                    }
                },
                "required": ["command"]
            }
        }
    }
]
 
GEMINI_TOOLS = [{"functionDeclarations": [
    {
        "name": "read_file",
        "description": "Reads the contents of a local file.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING", "description": "Absolute or relative path to the file to read."}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "write_file",
        "description": "Creates or overwrites a local file with content.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING", "description": "Path to the file."},
                "content": {"type": "STRING", "description": "Full content of the file."}
            },
            "required": ["filepath", "content"]
        }
    },
    {
        "name": "delete_file",
        "description": "Deletes a file or folder.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "filepath": {"type": "STRING", "description": "Path to delete."}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "list_directory",
        "description": "Lists the files and folders in a local directory.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "path": {"type": "STRING", "description": "Path to the directory, e.g. ./ or C:/path/to/folder"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "get_system_info",
        "description": "Gets the current system OS, Python version, current working directory, and local time.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "web_search",
        "description": "Searches the web for real-time information, latest documentation, or troubleshooting guides.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "The search query."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "run_shell_command",
        "description": "Executes a shell command on the host machine and returns stdout/stderr.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "command": {"type": "STRING", "description": "The shell command to execute."}
            },
            "required": ["command"]
        }
    }
]}]

def get_enabled_openai_tools(enabled_list):
    tools = [t for t in OPENAI_TOOLS if t['function']['name'] in enabled_list]
    return tools if tools else None

def get_enabled_gemini_tools(enabled_list):
    declarations = [d for d in GEMINI_TOOLS[0]['functionDeclarations'] if d['name'] in enabled_list]
    if not declarations:
        return None
    return [{"functionDeclarations": declarations}]
